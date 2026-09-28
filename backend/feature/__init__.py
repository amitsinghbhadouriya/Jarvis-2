"""
Feature module for Jarvis Assistant.
Exposes speech synthesis, recognition, audio feedback, and hotword detection.
"""

from .audio import (
    play_assistant_sound,
    play_success_sound,
    play_error_sound,
    speak,
    listen,
    get_audio_manager,
)
from .hotword import hotword, stop_hotword

__all__ = [
    "play_assistant_sound",
    "play_success_sound",
    "play_error_sound",
    "speak",
    "listen",
    "get_audio_manager",
    "hotword",
    "stop_hotword",
]
