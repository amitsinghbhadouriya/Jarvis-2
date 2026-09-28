"""
Configuration Management for Jarvis 2 Assistant.
Loads environment variables and sets system defaults.
"""

import os
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"


class AppConfig:
    """Application configuration container."""

    def __init__(
        self,
        app_name: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = None,
    ):
        # General
        self.app_name = app_name or os.getenv("APP_NAME", "Jarvis")
        self.app_env = os.getenv("APP_ENV", "development")
        self.host = os.getenv("APP_HOST", "localhost")
        self.port = port if port is not None else int(os.getenv("APP_PORT", "8000"))
        self.debug = (
            debug
            if debug is not None
            else os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
        )

        # Directory Paths
        self.base_dir = BASE_DIR
        self.frontend_dir = FRONTEND_DIR
        self.assets_dir = ASSETS_DIR
        self.audio_dir = AUDIO_DIR
        self.db_path = BASE_DIR / os.getenv("DB_NAME", "jarvis.db")

        # Audio Assets
        self.start_sound = self.audio_dir / "start_sound.wav"
        self.success_sound = self.audio_dir / "success_sound.wav"
        self.error_sound = self.audio_dir / "error_sound.wav"

        # Text-to-Speech (TTS)
        self.tts_rate = int(os.getenv("TTS_RATE", "175"))
        self.tts_volume = float(os.getenv("TTS_VOLUME", "0.9"))
        self.tts_voice_index = int(os.getenv("TTS_VOICE_INDEX", "0"))

        # Speech Recognition (STT)
        self.speech_timeout = int(os.getenv("SPEECH_TIMEOUT", "8"))
        self.speech_phrase_time_limit = int(os.getenv("SPEECH_PHRASE_TIME_LIMIT", "6"))
        self.speech_energy_threshold = int(os.getenv("SPEECH_ENERGY_THRESHOLD", "300"))
        self.hotword = os.getenv("HOTWORD", "jarvis").lower()

        # Face Authentication
        self.face_auth_enabled = os.getenv("FACE_AUTH_ENABLED", "True").lower() in (
            "true",
            "1",
            "yes",
        )
        self.face_auth_frames = int(os.getenv("FACE_AUTH_FRAMES", "30"))
        self.camera_index = int(os.getenv("CAMERA_INDEX", "0"))



# Global instance
config = AppConfig()
