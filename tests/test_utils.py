"""
Unit tests for system diagnostics, sanitization, and audio player utilities.
"""

from unittest.mock import patch
from backend.utils.system import sanitize_input, escape_html, get_system_status, launch_application
from backend.utils.audio_player import play_sound_file
from backend.config import config


def test_sanitize_input():
    """Verify input sanitization removes malicious tags and trims whitespace."""
    assert sanitize_input("  hello world  ") == "hello world"
    assert sanitize_input("<script>alert(1)</script>hi") == "hi"
    assert sanitize_input("<b>Bold</b> text") == "Bold text"
    assert sanitize_input("") == ""


def test_escape_html():
    """Verify HTML entity escaping."""
    assert escape_html("<script>") == "&lt;script&gt;"
    assert escape_html("A & B") == "A &amp; B"
    assert escape_html("") == ""


def test_system_status():
    """Verify system diagnostics return expected keys."""
    status = get_system_status()
    assert isinstance(status, dict)
    assert "os" in status
    assert "python_version" in status


def test_play_sound_nonexistent():
    """Verify non-existent sound returns False."""
    assert play_sound_file("non_existent_audio.wav") is False


def test_play_sound_valid():
    """Verify valid sound file invokes audio playback without error."""
    assert config.start_sound.exists()
    # Test playing without raising exception
    result = play_sound_file(config.start_sound, async_play=True)
    assert result is True


def test_launch_application():
    """Verify launch_application uses subprocess safely."""
    with patch("subprocess.Popen") as mock_popen:
        success = launch_application("notepad")
        assert success is True
        mock_popen.assert_called_once()
