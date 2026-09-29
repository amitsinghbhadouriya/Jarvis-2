"""
Unit tests for YouTube playback and video media controls.
"""

from unittest.mock import patch
from backend.command.handlers.media_handler import (
    handle_play_youtube,
    handle_media_control,
)
from backend.command.dispatcher import process_command


def test_play_youtube_homepage():
    """Verify empty topic opens YouTube homepage."""
    with patch("webbrowser.open") as mock_open:
        res = handle_play_youtube("open youtube")
        assert "Opening YouTube" in res
        mock_open.assert_called_once_with("https://www.youtube.com")


def test_play_youtube_with_topic():
    """Verify pywhatkit is called to play video directly."""
    with patch("pywhatkit.playonyt") as mock_play:
        res = handle_play_youtube("play hale dil song on youtube")
        assert "Playing 'hale dil song' on YouTube" in res
        mock_play.assert_called_once_with("hale dil song")


def test_play_youtube_pywhatkit_fallback():
    """Verify fallback when pywhatkit raises exception."""
    with patch("pywhatkit.playonyt", side_effect=RuntimeError("pywhatkit error")), patch(
        "backend.command.handlers.media_handler.find_youtube_video_url",
        return_value="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ), patch("webbrowser.open") as mock_open:
        res = handle_play_youtube("play never gonna give you up")
        assert "Playing 'never gonna give you up' on YouTube" in res
        mock_open.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


def test_media_control_pause():
    """Verify pause command dispatches keyboard shortcut."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("pause video")
        assert res == "Video paused."
        mock_press.assert_called_once_with("k")


def test_media_control_resume():
    """Verify resume command dispatches keyboard shortcut."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("resume video")
        assert res == "Video resumed."
        mock_press.assert_called_once_with("k")


def test_media_control_mute():
    """Verify mute command toggles audio shortcut."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("mute video")
        assert "audio toggled" in res
        mock_press.assert_called_once_with("m")


def test_media_control_fullscreen():
    """Verify fullscreen command toggles f shortcut."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("toggle fullscreen")
        assert "Fullscreen mode toggled" in res
        mock_press.assert_called_once_with("f")


def test_media_control_volume_up():
    """Verify volume up command presses up arrow."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("increase volume")
        assert "volume increased" in res
        assert mock_press.call_args[0][0] == "up"


def test_media_control_volume_down():
    """Verify volume down command presses down arrow."""
    with patch("pyautogui.press") as mock_press:
        res = handle_media_control("decrease volume")
        assert "volume decreased" in res
        assert mock_press.call_args[0][0] == "down"


def test_media_control_skip_next():
    """Verify next video uses shift+n shortcut."""
    with patch("pyautogui.hotkey") as mock_hotkey:
        res = handle_media_control("next video")
        assert "Skipping to the next video" in res
        mock_hotkey.assert_called_once_with("shift", "n")


def test_media_control_previous():
    """Verify previous video uses shift+p shortcut."""
    with patch("pyautogui.hotkey") as mock_hotkey:
        res = handle_media_control("previous video")
        assert "Returning to previous video" in res
        mock_hotkey.assert_called_once_with("shift", "p")


def test_media_control_close_video():
    """Verify stop video closes active tab with ctrl+w."""
    with patch("pyautogui.hotkey") as mock_hotkey:
        res = handle_media_control("stop video")
        assert "Video closed" in res
        mock_hotkey.assert_called_once_with("ctrl", "w")


def test_dispatcher_media_routing():
    """Verify command dispatcher routes pause and play queries properly."""
    with patch("pyautogui.press"):
        res = process_command("pause video")
        assert "Video paused" in res

    with patch("pywhatkit.playonyt"):
        res = process_command("play believer on youtube")
        assert "Playing 'believer' on YouTube" in res


def test_ad_skipper_singleton_and_toggle():
    """Verify YouTubeAdSkipper state management."""
    from backend.feature.ad_skipper import ad_skipper

    assert ad_skipper.is_enabled is True
    ad_skipper.set_enabled(False)
    assert ad_skipper.is_enabled is False
    ad_skipper.set_enabled(True)
    assert ad_skipper.is_enabled is True


def test_ad_skipper_skip_now():
    """Verify skip_ad_now dispatches keyboard focus and click sequence."""
    from backend.feature.ad_skipper import ad_skipper

    with patch("pyautogui.press") as mock_press, patch("pyautogui.click") as mock_click, patch(
        "pyautogui.size", return_value=(1920, 1080)
    ):
        success = ad_skipper.skip_ad_now()
        assert success is True
        assert mock_press.call_count >= 2
        assert mock_click.call_count >= 1


def test_media_control_skip_ad():
    """Verify media control routing for skip ad command."""
    with patch("backend.feature.ad_skipper.ad_skipper.skip_ad_now") as mock_skip:
        res = handle_media_control("skip ad")
        assert "skip youtube ad" in res.lower() or "skipped" in res.lower()
        mock_skip.assert_called_once()


def test_play_youtube_ad_free_embed():
    """Verify ad-free request routes to embed URL."""
    with patch("backend.command.handlers.media_handler.find_youtube_video_url", return_value="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), patch(
        "webbrowser.open"
    ) as mock_open:
        res = handle_play_youtube("play song ad free")
        assert "ad-free embedded mode" in res
        mock_open.assert_called_once_with("https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1")

