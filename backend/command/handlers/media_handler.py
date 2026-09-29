"""
Media and Video Playback Controller for Jarvis 2.
Enables automatic YouTube video playback and keyboard-driven media control.
"""

import re
import urllib.parse
import urllib.request
import webbrowser
from typing import Optional
from backend.logger import get_logger

logger = get_logger("MediaHandler")


def find_youtube_video_url(topic: str) -> Optional[str]:
    """Search YouTube and scrape the first valid video watch URL."""
    clean_topic = topic.strip()
    if not clean_topic:
        return None

    try:
        encoded = urllib.parse.quote_plus(clean_topic)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=4.0) as response:
            html = response.read().decode("utf-8", errors="ignore")
            # Extract 11-character video IDs from YouTube watch links
            video_ids = re.findall(r"/watch\?v=([a-zA-Z0-9_-]{11})", html)
            if video_ids:
                return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        logger.debug(f"Direct YouTube scrape notice for '{clean_topic}': {e}")

    return None


def handle_play_youtube(query: str) -> str:
    """
    Play a requested video or song directly on YouTube instead of just searching.
    Uses pywhatkit with fast regex-scrape fallback.
    """
    cleaned = re.sub(
        r"^(play\s+a\s+video\s+on\s+youtube|play\s+on\s+youtube|play\s+video|play\s+song|play\s+music|open\s+youtube|play|watch)\s*",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(r"\s+on\s+youtube$", "", cleaned, flags=re.IGNORECASE).strip()

    # If no topic specified, open the YouTube homepage
    if not cleaned or cleaned.lower() in ["youtube", "video", "a video"]:
        try:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."
        except Exception as e:
            return f"Failed to open YouTube: {e}"

    from backend.feature.ad_skipper import ad_skipper

    # Check for explicit ad-free embedded request
    ad_free_requested = bool(re.search(r"\b(ad\s*free|no\s*ads|without\s*ads)\b", query, re.IGNORECASE))
    cleaned = re.sub(r"\b(ad\s*free|no\s*ads|without\s*ads)\b", "", cleaned, flags=re.IGNORECASE).strip()

    # Try pywhatkit playonyt first if standard mode
    video_url = None
    if not ad_free_requested:
        try:
            import pywhatkit

            logger.info(f"Playing video on YouTube via pywhatkit: '{cleaned}'")
            pywhatkit.playonyt(cleaned)
            ad_skipper.start_monitoring(duration_minutes=20)
            return f"Playing '{cleaned}' on YouTube with automatic ad-skipping active."
        except Exception as e:
            logger.warning(f"pywhatkit playonyt exception: {e}. Falling back to direct URL resolution.")

    # Direct scrape and play
    video_url = find_youtube_video_url(cleaned)
    if video_url:
        try:
            if ad_free_requested:
                # Use clean embedded player that bypasses prerolls and midrolls
                video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", video_url)
                if video_id_match:
                    video_url = f"https://www.youtube.com/embed/{video_id_match.group(1)}?autoplay=1"
            webbrowser.open(video_url)
            ad_skipper.start_monitoring(duration_minutes=20)
            mode_desc = "ad-free embedded mode" if ad_free_requested else "with automatic ad-skipping active"
            return f"Playing '{cleaned}' on YouTube ({mode_desc})."
        except Exception as e:
            logger.error(f"Error opening video URL: {e}")

    # Fallback to search query
    encoded = urllib.parse.quote_plus(cleaned)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    try:
        webbrowser.open(search_url)
        ad_skipper.start_monitoring(duration_minutes=20)
        return f"Opening YouTube results for '{cleaned}'."
    except Exception as e:
        return f"Could not open YouTube for '{cleaned}': {e}"


def handle_media_control(command: str) -> Optional[str]:
    """
    Control active video playback (pause, resume, mute, fullscreen, skip, volume, stop).
    Uses pyautogui and ad_skipper to dispatch commands.
    """
    from backend.feature.ad_skipper import ad_skipper

    lowered = command.strip().lower()

    # Skip Ad Commands
    if any(w in lowered for w in ["skip ad", "skip the ad", "skip ads", "skip youtube ad", "bypass ad"]):
        ad_skipper.skip_ad_now()
        return "Attempted to skip YouTube ad."

    if any(w in lowered for w in ["enable ad skipper", "turn on ad skipper", "start ad skipper"]):
        ad_skipper.set_enabled(True)
        ad_skipper.start_monitoring(duration_minutes=25)
        return "Automatic ad-skipper enabled and monitoring."

    if any(w in lowered for w in ["disable ad skipper", "turn off ad skipper", "stop ad skipper"]):
        ad_skipper.set_enabled(False)
        return "Automatic ad-skipper disabled."

    try:
        import pyautogui
    except ImportError:
        logger.warning("pyautogui is not installed; media control hotkeys unavailable.")
        return "Media control requires the pyautogui library."

    try:
        # Pause Video
        if any(w in lowered for w in ["pause video", "pause the video", "pause song", "pause youtube"]) or lowered == "pause":
            pyautogui.press("k")
            return "Video paused."

        # Resume / Play Video
        elif any(w in lowered for w in ["resume video", "resume the video", "resume song", "continue video"]) or lowered in ["resume", "unpause"]:
            pyautogui.press("k")
            return "Video resumed."

        # Mute / Unmute
        elif any(w in lowered for w in ["mute video", "unmute video", "mute youtube", "unmute youtube", "mute audio", "unmute audio"]) or lowered in ["mute", "unmute"]:
            pyautogui.press("m")
            return "Video audio toggled."

        # Fullscreen
        elif any(w in lowered for w in ["fullscreen", "full screen", "toggle fullscreen", "exit fullscreen"]):
            pyautogui.press("f")
            return "Fullscreen mode toggled."

        # Volume Up
        elif any(w in lowered for w in ["volume up", "increase volume", "raise volume", "louder"]):
            pyautogui.press("up", presses=3, interval=0.08)
            return "Video volume increased."

        # Volume Down
        elif any(w in lowered for w in ["volume down", "decrease volume", "lower volume", "quieter"]):
            pyautogui.press("down", presses=3, interval=0.08)
            return "Video volume decreased."

        # Forward / Skip Ahead
        elif any(w in lowered for w in ["forward", "fast forward", "skip 10 seconds", "forward 10 seconds"]):
            pyautogui.press("l")
            return "Skipped forward 10 seconds."

        # Rewind
        elif any(w in lowered for w in ["rewind", "rewind 10 seconds", "go back 10 seconds"]):
            pyautogui.press("j")
            return "Rewound 10 seconds."

        # Next Video
        elif any(w in lowered for w in ["next video", "next song", "skip video", "skip song"]):
            pyautogui.hotkey("shift", "n")
            return "Skipping to the next video."

        # Previous Video
        elif any(w in lowered for w in ["previous video", "previous song", "last video"]):
            pyautogui.hotkey("shift", "p")
            return "Returning to previous video."

        # Stop / Close Video
        elif any(w in lowered for w in ["stop video", "close video", "stop youtube", "close youtube", "stop playing"]):
            ad_skipper.stop_monitoring()
            pyautogui.hotkey("ctrl", "w")
            return "Video closed."

    except Exception as e:
        logger.error(f"Error executing media control hotkey: {e}")
        return f"Unable to control media: {e}"

    return None
