"""
Unit tests for configuration manager and directory resolution.
"""

from backend.config import AppConfig, config


def test_config_defaults():
    """Verify default configuration values."""
    assert config.app_name == "Jarvis"
    assert config.port == 8000
    assert config.tts_rate > 0
    assert config.tts_volume > 0.0
    assert config.hotword == "jarvis"


def test_config_paths_exist():
    """Verify core paths resolve properly."""
    assert config.base_dir.exists()
    assert config.frontend_dir.exists()
    assert config.assets_dir.exists()
    assert config.audio_dir.exists()


def test_custom_config_override(monkeypatch):
    """Verify environment variable overrides."""
    monkeypatch.setenv("APP_NAME", "JarvisTest")
    monkeypatch.setenv("APP_PORT", "9090")
    custom_cfg = AppConfig()
    assert custom_cfg.app_name == "JarvisTest"
    assert custom_cfg.port == 9090
