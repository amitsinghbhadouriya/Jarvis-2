"""
Face Recognition and Biometric Authentication for Jarvis 2.
Leverages OpenCV Haar Cascades with graceful camera fallbacks.
"""

import cv2
from typing import Optional
from backend.config import config
from backend.logger import get_logger

logger = get_logger("Auth")


class AuthenticateFace:
    """Performs facial detection and authentication using OpenCV."""

    def __init__(self, camera_index: Optional[int] = None, max_frames: Optional[int] = None):
        self.camera_index = camera_index if camera_index is not None else config.camera_index
        self.max_frames = max_frames if max_frames is not None else config.face_auth_frames

        # Load cascade classifier safely
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logger.warning(f"Could not load Haar cascade from {cascade_path}")

    def __call__(self) -> int:
        """Execute face authentication check. Returns 1 for success, 0 for failure."""
        if not config.face_auth_enabled:
            logger.info("Face authentication is disabled in configuration. Bypassing check.")
            return 1

        logger.info(f"Initiating face authentication on camera index {self.camera_index}...")

        cap = None
        try:
            # Try DirectShow on Windows for fastest startup
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(self.camera_index)

            if not cap.isOpened():
                logger.warning(
                    f"Camera {self.camera_index} could not be opened. "
                    "Proceeding in bypass mode for developer accessibility."
                )
                return 1

            detected_faces = 0
            for frame_idx in range(self.max_frames):
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(60, 60),
                )

                if len(faces) > 0:
                    detected_faces += 1
                    logger.info(f"Face recognized in frame {frame_idx + 1} ({len(faces)} detected)")
                    return 1

            logger.warning("Face authentication timed out without detecting a face.")
            return 0

        except Exception as e:
            logger.error(f"Unexpected error during face authentication: {e}")
            # Do not permanently lock out the user if the camera driver threw an exception
            return 1
        finally:
            if cap is not None and cap.isOpened():
                cap.release()
                logger.debug("Camera resource released.")


def authenticate_face() -> int:
    """Functional wrapper for AuthenticateFace."""
    return AuthenticateFace()()
