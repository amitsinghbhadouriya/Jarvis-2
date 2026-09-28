"""
Unit tests for facial authentication and OpenCV cascade handling.
"""

from unittest.mock import MagicMock, patch
from backend.auth.recognize import AuthenticateFace, authenticate_face
from backend.config import config


def test_auth_disabled_bypass(monkeypatch):
    """Verify that disabling face authentication in config bypasses check."""
    monkeypatch.setattr(config, "face_auth_enabled", False)
    auth = AuthenticateFace()
    assert auth() == 1


def test_auth_camera_unavailable(monkeypatch):
    """Verify graceful fallback when camera device cannot be opened."""
    monkeypatch.setattr(config, "face_auth_enabled", True)
    with patch("cv2.VideoCapture") as mock_cap:
        instance = MagicMock()
        instance.isOpened.return_value = False
        mock_cap.return_value = instance

        auth = AuthenticateFace()
        # When camera is unavailable, returns 1 for developer accessibility
        assert auth() == 1


def test_auth_face_detected(monkeypatch):
    """Verify face detection returns 1 upon positive frame match."""
    monkeypatch.setattr(config, "face_auth_enabled", True)
    with patch("cv2.VideoCapture") as mock_cap:
        instance = MagicMock()
        instance.isOpened.return_value = True
        # Mock valid frame read
        import numpy as np

        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        instance.read.return_value = (True, dummy_frame)
        mock_cap.return_value = instance

        with patch("cv2.CascadeClassifier.detectMultiScale") as mock_detect:
            # Simulate detected face rectangle: [x, y, w, h]
            mock_detect.return_value = [[10, 10, 50, 50]]
            auth = AuthenticateFace(max_frames=5)
            assert auth() == 1


def test_auth_functional_wrapper():
    """Verify authenticate_face functional wrapper."""
    with patch.object(AuthenticateFace, "__call__", return_value=1):
        assert authenticate_face() == 1
