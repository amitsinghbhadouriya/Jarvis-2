"""
Hotword detection module for Jarvis 2.
Listens continuously in a background loop for the wake word.
"""

import time
import speech_recognition as sr
from backend.config import config
from backend.logger import get_logger

logger = get_logger("Hotword")
_hotword_active = True


def stop_hotword() -> None:
    """Signal hotword detection loop to terminate."""
    global _hotword_active
    _hotword_active = False
    logger.info("Hotword listening flagged to stop.")


def hotword() -> None:
    """
    Continuous hotword detection loop.
    Monitors audio stream for the configured wake word.
    """
    global _hotword_active
    _hotword_active = True
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = config.speech_energy_threshold
    recognizer.dynamic_energy_threshold = True

    target_word = config.hotword.lower()
    logger.info(f"Hotword daemon active. Listening for keyword: '{target_word}'...")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            while _hotword_active:
                try:
                    audio = recognizer.listen(source, timeout=3.0, phrase_time_limit=4.0)
                    recognized = recognizer.recognize_google(audio).lower()
                    logger.debug(f"[Hotword Ambient]: {recognized}")
                    if target_word in recognized:
                        logger.info(f"Wake word '{target_word}' detected in phrase: '{recognized}'")
                        from backend.feature.audio import play_assistant_sound
                        play_assistant_sound()
                except sr.WaitTimeoutError:
                    continue
                except (sr.UnknownValueError, sr.RequestError):
                    continue
                except Exception as e:
                    logger.debug(f"Transient listening notice: {e}")
                    time.sleep(0.5)

    except OSError as e:
        logger.warning(f"Microphone unavailable for hotword detection: {e}")
    except Exception as e:
        logger.error(f"Fatal error in hotword detection loop: {e}")
    finally:
        logger.info("Hotword listener terminated cleanly.")
