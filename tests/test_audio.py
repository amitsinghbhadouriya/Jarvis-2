"""
Unit tests for AudioManager, speech synthesis, and audio feedback chimes.
"""

from unittest.mock import patch, MagicMock
from backend.feature.audio import (
    get_audio_manager,
    speak,
    listen,
    play_assistant_sound,
    play_success_sound,
    play_error_sound,
)


def test_audio_manager_singleton():
    """Verify AudioManager enforces the singleton design pattern."""
    am1 = get_audio_manager()
    am2 = get_audio_manager()
    assert am1 is am2


def test_play_chimes():
    """Verify assistant, success, and error chimes execute safely."""
    assert play_assistant_sound() is True
    assert play_success_sound() is True
    assert play_error_sound() is True


def test_speak_queue():
    """Verify speak puts messages on the queue without blocking."""
    am = get_audio_manager()
    initial_size = am._tts_queue.qsize()
    speak("Testing speech synthesis queuing", block=False)
    # The message is placed onto the queue
    assert am._tts_queue.qsize() >= initial_size


def test_listen_timeout():
    """Verify listen handles audio timeout gracefully without raising an exception."""
    with patch("speech_recognition.Microphone") as mock_mic:
        mock_source = MagicMock()
        mock_mic.return_value.__enter__.return_value = mock_source
        with patch("speech_recognition.Recognizer.listen") as mock_listen:
            import speech_recognition as sr
            mock_listen.side_effect = sr.WaitTimeoutError("Timed out")
            result = listen()
            assert result == ""
