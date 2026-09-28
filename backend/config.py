"""
Configuration Management for Jarvis 2 Assistant.
Loads environment variables and sets system defaults.
"""

import os
from pathlib import Path
from dataclasses import dataclass


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"


@dataclass
class AppConfig:
    """Application configuration container."""

    # General
    app_name: str = "Jarvis"
    app_env: str = os.getenv("APP_ENV", "development")
    host: str = os.getenv("APP_HOST", "localhost")
    port: int = int(os.getenv("APP_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Directory Paths
    base_dir: Path = BASE_DIR
    frontend_dir: Path = FRONTEND_DIR
    assets_dir: Path = ASSETS_DIR
    audio_dir: Path = AUDIO_DIR
    db_path: Path = BASE_DIR / os.getenv("DB_NAME", "jarvis.db")

    # Audio Assets
    start_sound: Path = AUDIO_DIR / "start_sound.wav"
    success_sound: Path = AUDIO_DIR / "success_sound.wav"
    error_sound: Path = AUDIO_DIR / "error_sound.wav"

    # Text-to-Speech (TTS)
    tts_rate: int = int(os.getenv("TTS_RATE", "175"))
    tts_volume: float = float(os.getenv("TTS_VOLUME", "0.9"))
    tts_voice_index: int = int(os.getenv("TTS_VOICE_INDEX", "0"))

    # Speech Recognition (STT)
    speech_timeout: int = int(os.getenv("SPEECH_TIMEOUT", "8"))
    speech_phrase_time_limit: int = int(os.getenv("SPEECH_PHRASE_TIME_LIMIT", "6"))
    speech_energy_threshold: int = int(os.getenv("SPEECH_ENERGY_THRESHOLD", "300"))
    hotword: str = os.getenv("HOTWORD", "jarvis").lower()

    # Face Authentication
    face_auth_enabled: bool = os.getenv("FACE_AUTH_ENABLED", "True").lower() in ("true", "1", "yes")
    face_auth_frames: int = int(os.getenv("FACE_AUTH_FRAMES", "30"))
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))


# Global instance
config = AppConfig()
