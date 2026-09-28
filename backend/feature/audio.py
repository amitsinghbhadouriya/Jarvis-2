"""
Audio and Speech Processing Module for Jarvis 2.
Handles Text-to-Speech (TTS), Speech-to-Text (STT), and audio chime playback.
"""

import sys
import queue
import threading
from typing import Optional
import speech_recognition as sr
from backend.config import config
from backend.logger import get_logger
from backend.utils.audio_player import play_sound_file

logger = get_logger("Audio")


class AudioManager:
    """Central manager for speech synthesis, voice recognition, and sound effects."""

    _instance: Optional["AudioManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "AudioManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._tts_queue: queue.Queue = queue.Queue()
        self._running = True
        self._tts_worker = threading.Thread(target=self._tts_loop, daemon=True)
        self._tts_worker.start()
        self._initialized = True
        logger.info("AudioManager initialized.")

    def _tts_loop(self) -> None:
        """Background worker thread consuming and speaking TTS messages."""
        engine = None
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", config.tts_rate)
            engine.setProperty("volume", config.tts_volume)
            voices = engine.getProperty("voices")
            if voices and 0 <= config.tts_voice_index < len(voices):
                engine.setProperty("voice", voices[config.tts_voice_index].id)
        except Exception as e:
            logger.warning(f"pyttsx3 engine initialization warning: {e}")
            engine = None

        while self._running:
            try:
                item = self._tts_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if item is None:
                break

            text, done_event = item
            logger.info(f"[Speech Output]: {text}")
            if engine:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS playback error: {e}")
            self._tts_queue.task_done()
            if done_event:
                done_event.set()

    def speak(self, text: str, block: bool = False) -> None:
        """Speak a text message using TTS."""
        if not text or not text.strip():
            return
        done_event = threading.Event() if block else None
        self._tts_queue.put((text.strip(), done_event))
        if block and done_event:
            done_event.wait(timeout=15.0)

    def listen(self) -> str:
        """Listen for voice input using the microphone and return recognized text."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = config.speech_energy_threshold
        recognizer.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                logger.info("Calibrating ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                logger.info("Listening for user input...")
                audio = recognizer.listen(
                    source,
                    timeout=config.speech_timeout,
                    phrase_time_limit=config.speech_phrase_time_limit,
                )

            logger.info("Processing voice audio via Google STT...")
            text = recognizer.recognize_google(audio)
            logger.info(f"[Recognized Voice]: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.debug("Voice listening timed out (no speech detected).")
            return ""
        except sr.UnknownValueError:
            logger.info("Speech was unintelligible.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return ""
        except OSError as e:
            logger.warning(f"Microphone device unavailable: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error during speech recognition: {e}")
            return ""

    def play_assistant_sound(self) -> bool:
        """Play assistant activation sound effect."""
        return play_sound_file(config.start_sound)

    def play_success_sound(self) -> bool:
        """Play confirmation sound effect."""
        return play_sound_file(config.success_sound)

    def play_error_sound(self) -> bool:
        """Play error alert sound effect."""
        return play_sound_file(config.error_sound)


# Module-level convenience functions
def get_audio_manager() -> AudioManager:
    """Retrieve the singleton AudioManager instance."""
    return AudioManager()


def speak(message: str, block: bool = False) -> None:
    """Speak text output through the default speech engine."""
    get_audio_manager().speak(message, block=block)


def listen() -> str:
    """Capture speech input from the microphone."""
    return get_audio_manager().listen()


def play_assistant_sound() -> bool:
    """Play assistant startup chime."""
    return get_audio_manager().play_assistant_sound()


def play_success_sound() -> bool:
    """Play success chime."""
    return get_audio_manager().play_success_sound()


def play_error_sound() -> bool:
    """Play error chime."""
    return get_audio_manager().play_error_sound()
