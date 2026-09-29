"""
Automatic YouTube Ad Skipper Daemon for Jarvis 2.
Monitors video playback and automatically dismisses pre-roll, mid-roll, and overlay ads.
"""

import time
import threading
from typing import Optional, Tuple
from backend.logger import get_logger

logger = get_logger("AdSkipper")


class YouTubeAdSkipper:
    """Background daemon to detect and automatically skip YouTube ads."""

    _instance: Optional["YouTubeAdSkipper"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "YouTubeAdSkipper":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(YouTubeAdSkipper, cls).__new__(cls)
                cls._instance._monitoring = False
                cls._instance._thread = None
                cls._instance._enabled = True
                cls._instance._stop_event = threading.Event()
            return cls._instance

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @property
    def is_monitoring(self) -> bool:
        return self._monitoring

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self.stop_monitoring()

    def start_monitoring(self, duration_minutes: int = 20) -> None:
        """Start background ad-skipping loop for the specified video duration."""
        if not self._enabled:
            return

        with self._lock:
            self._stop_event.clear()
            if self._thread and self._thread.is_alive():
                return

            self._monitoring = True
            self._thread = threading.Thread(
                target=self._monitor_loop,
                args=(duration_minutes,),
                daemon=True,
                name="JarvisAdSkipper",
            )
            self._thread.start()
            logger.info(f"YouTube Ad Skipper active. Monitoring for {duration_minutes} minutes.")

    def stop_monitoring(self) -> None:
        """Stop background ad-skipping thread."""
        self._stop_event.set()
        self._monitoring = False
        logger.info("YouTube Ad Skipper stopped.")

    def skip_ad_now(self) -> bool:
        """
        Manually trigger immediate ad skip via keyboard shortcuts and click targets.
        Returns True if action was executed.
        """
        try:
            import pyautogui

            # Check if button is detected on screen
            button_loc = self.locate_skip_button()
            if button_loc:
                x, y = button_loc
                pyautogui.click(x, y)
                logger.info(f"Clicked detected Skip Ad button at ({x}, {y})")
                return True

            # Fallback 1: YouTube player skip shortcut (Tab focuses skip button, Enter activates)
            pyautogui.press("tab")
            pyautogui.press("enter")

            # Fallback 2: Common skip coordinates in YouTube desktop player
            screen_w, screen_h = pyautogui.size()
            candidate_points = [
                (int(screen_w * 0.85), int(screen_h * 0.78)),
                (int(screen_w * 0.82), int(screen_h * 0.74)),
                (int(screen_w * 0.88), int(screen_h * 0.81)),
                (int(screen_w * 0.90), int(screen_h * 0.76)),
            ]
            for x, y in candidate_points:
                pyautogui.click(x, y)
                time.sleep(0.04)

            logger.info("Dispatched ad-skip sequence.")
            return True
        except Exception as e:
            logger.error(f"Error skipping ad: {e}")
            return False

    def locate_skip_button(self) -> Optional[Tuple[int, int]]:
        """Scan candidate screen region using OpenCV to identify the Skip Ad button."""
        try:
            import pyautogui
            import cv2
            import numpy as np

            screen_w, screen_h = pyautogui.size()
            # Region: bottom-right quadrant where YouTube renders skip ad button
            left = int(screen_w * 0.65)
            top = int(screen_h * 0.55)
            width = int(screen_w * 0.32)
            height = int(screen_h * 0.35)

            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)

            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                approx = cv2.approxPolyDP(cnt, 0.03 * cv2.arcLength(cnt, True), True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / max(1, h)
                    # Skip button is roughly 1.8 to 5.0 aspect ratio
                    if 1.8 <= aspect_ratio <= 5.0 and 55 <= w <= 240 and 22 <= h <= 65:
                        abs_x = left + x + w // 2
                        abs_y = top + y + h // 2
                        return (abs_x, abs_y)
        except Exception as e:
            logger.debug(f"Template/contour search notice: {e}")
        return None

    def _monitor_loop(self, duration_minutes: int) -> None:
        """Background loop scanning and clicking skip buttons as ads appear."""
        start_time = time.time()
        max_duration = duration_minutes * 60

        while not self._stop_event.is_set():
            if time.time() - start_time > max_duration:
                break

            try:
                loc = self.locate_skip_button()
                if loc:
                    import pyautogui

                    x, y = loc
                    pyautogui.click(x, y)
                    logger.info(f"[AdSkipper]: Automatically clicked Skip Ad at ({x}, {y})")
                    time.sleep(2.0)
            except Exception as e:
                logger.debug(f"Ad monitor iteration notice: {e}")

            time.sleep(1.2)

        self._monitoring = False
        logger.info("Ad monitor loop ended.")


# Global singleton helper
ad_skipper = YouTubeAdSkipper()
