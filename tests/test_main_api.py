"""
Unit tests for Eel RPC API endpoints and communication pipeline.
"""

from unittest.mock import patch, MagicMock
from main import (
    send_message,
    voice_input,
    takeAllCommands,
    getChatHistory,
    clearChatHistory,
    getSystemTelemetry,
    safe_eel_call,
)


def test_safe_eel_call_nonexistent():
    """Verify safe_eel_call handles missing attributes without raising errors."""
    safe_eel_call("some_completely_nonexistent_function_123")


def test_safe_eel_call_existing():
    """Verify safe_eel_call invokes callable when present."""
    mock_fn = MagicMock()
    with patch("main.eel") as mock_eel:
        mock_eel.test_func = mock_fn
        safe_eel_call("test_func", "arg1", 42)
        mock_fn.assert_called_once_with("arg1", 42)


def test_send_message_empty():
    """Verify empty message validation."""
    res = send_message("")
    assert res["success"] is False
    assert res["error"] == "Empty message"

    res_spaces = send_message("    ")
    assert res_spaces["success"] is False
    assert res_spaces["error"] == "Empty message"


def test_send_message_valid_text():
    """Verify text message processing and response structure."""
    with patch("main.speak") as mock_speak:
        res = send_message("what time is it?", source="text")
        assert res["success"] is True
        assert res["user_message"] == "what time is it?"
        assert "current time is" in res["response"].lower()
        assert res["source"] == "text"
        assert "timestamp" in res
        mock_speak.assert_called_once()


def test_send_message_exception_handling():
    """Verify error containment if dispatcher or downstream fails."""
    with patch("main.process_command", side_effect=RuntimeError("Test error")):
        res = send_message("test command")
        assert res["success"] is False
        assert "Test error" in res["error"]
        assert "error processing message" in res["response"].lower()


def test_voice_input_empty():
    """Verify voice_input returns error when no speech is detected."""
    with patch("main.listen", return_value=""):
        res = voice_input()
        assert res["success"] is False
        assert res["error"] == "No speech detected"


def test_voice_input_success():
    """Verify voice_input processes audio transcript and returns structured response."""
    with patch("main.listen", return_value="what is today's date?"), patch("main.speak"):
        res = voice_input()
        assert res["success"] is True
        assert res["source"] == "voice"
        assert res["transcript"] == "what is today's date?"
        assert "today is" in res["response"].lower()


def test_take_all_commands_text_route():
    """Verify takeAllCommands routes text properly."""
    with patch("main.speak"):
        res = takeAllCommands("tell me a joke")
        assert res["success"] is True
        assert res["source"] == "text"


def test_take_all_commands_voice_route():
    """Verify takeAllCommands routes empty/None to voice_input."""
    with patch("main.listen", return_value="help"), patch("main.speak"):
        res = takeAllCommands(None)
        assert res["success"] is True
        assert res["source"] == "voice"


def test_chat_history_and_clear():
    """Verify getChatHistory and clearChatHistory work as expected."""
    history = getChatHistory(limit=5)
    assert isinstance(history, list)

    cleared = clearChatHistory()
    assert cleared is True


def test_system_telemetry():
    """Verify telemetry returns system metrics dict."""
    telemetry = getSystemTelemetry()
    assert isinstance(telemetry, dict)
    assert "os" in telemetry
    assert "python_version" in telemetry

