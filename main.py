"""
Jarvis 2 - Main Application Controller
Orchestrates Eel GUI, facial authentication, speech processing, and command pipeline.
"""

import sys
import time
import subprocess
import webbrowser
import eel
from backend.config import config
from backend.logger import get_logger
from backend.auth.recognize import authenticate_face
from backend.feature.audio import (
    play_assistant_sound,
    play_success_sound,
    play_error_sound,
    speak,
    listen,
)
from backend.command.dispatcher import process_command
from backend.database import get_recent_history, clear_history, set_setting, get_setting
from backend.utils.system import get_system_status

logger = get_logger("Main")


def launch_browser_app(url: str) -> None:
    """Launch the application window in Edge/Chrome app mode or system browser."""
    if sys.platform == "win32":
        try:
            # Try launching Edge in dedicated app mode
            subprocess.Popen(["msedge.exe", f"--app={url}"], shell=False)
            return
        except Exception:
            try:
                # Try Chrome in dedicated app mode
                subprocess.Popen(["chrome.exe", f"--app={url}"], shell=False)
                return
            except Exception:
                pass
    # Fallback to default system browser
    webbrowser.open(url)


def safe_eel_call(func_name: str, *args, **kwargs) -> None:
    """Safely invoke an Eel JS function if available, preventing crashes if client is not connected."""
    try:
        fn = getattr(eel, func_name, None)
        if fn and callable(fn):
            fn(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Eel JS call '{func_name}' skipped: {e}")


@eel.expose
def play_assistant_sound_effect() -> None:
    """Trigger assistant chime audio."""
    play_assistant_sound()


@eel.expose
def init() -> None:
    """Initialize GUI after page load and execute face authentication."""
    try:
        logger.info("Starting authentication flow...")
        safe_eel_call("hideLoader")
        speak("Welcome to Jarvis. Initiating facial authentication.")

        flag = authenticate_face()
        if flag == 1:
            speak("Face recognized successfully.")
            play_success_sound()
            time.sleep(0.8)
            safe_eel_call("hideFaceAuth")
            time.sleep(0.5)
            safe_eel_call("hideFaceAuthSuccess")
            time.sleep(1.0)
            speak("Welcome back. Jarvis online and awaiting commands.")
            safe_eel_call("hideStart")
            play_assistant_sound()
        else:
            speak("Authentication failed. Please verify camera positioning.")
            play_error_sound()
            time.sleep(1.0)
            safe_eel_call("hideFaceAuth")
            safe_eel_call("hideStart")
    except Exception as e:
        logger.error(f"Error during init flow: {e}")
        safe_eel_call("hideLoader")
        safe_eel_call("hideStart")


@eel.expose
def send_message(message: str, source: str = "text", mute: bool = False) -> dict:
    """
    Send text or transcribed voice message to Jarvis.
    Returns predictable structured dictionary and triggers bidirectional UI updates.
    """
    import datetime

    clean_text = str(message or "").strip()
    timestamp_str = datetime.datetime.now().strftime("%I:%M %p")

    if not clean_text:
        return {
            "success": False,
            "error": "Empty message",
            "timestamp": timestamp_str,
        }

    try:
        logger.info(f"[Message Received] ({source}, mute={mute}): '{clean_text}'")

        # 1. Update UI with user message
        safe_eel_call("senderText", clean_text, timestamp_str)

        # 2. Show typing indicator
        safe_eel_call("setAssistantTyping", True)

        # 3. Process command
        reply = process_command(clean_text, source=source)

        # 4. Hide typing indicator & push assistant response to UI
        safe_eel_call("setAssistantTyping", False)
        safe_eel_call("receiverText", reply, timestamp_str)
        safe_eel_call("DisplayMessage", reply[:60] + ("..." if len(reply) > 60 else ""))

        # 5. Speak response asynchronously if voice output is not muted
        if not mute:
            speak(reply, block=False)

        return {
            "success": True,
            "user_message": clean_text,
            "response": reply,
            "source": source,
            "timestamp": timestamp_str,
        }

    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        error_reply = f"Error processing message: {str(e)}"
        safe_eel_call("setAssistantTyping", False)
        safe_eel_call("receiverText", error_reply, timestamp_str)
        return {
            "success": False,
            "error": str(e),
            "response": error_reply,
            "timestamp": timestamp_str,
        }


@eel.expose
def voice_input() -> dict:
    """
    Trigger microphone capture on backend, transcribe, and dispatch to Jarvis.
    """
    import datetime

    timestamp_str = datetime.datetime.now().strftime("%I:%M %p")
    try:
        safe_eel_call("updateStatus", "Listening...")
        safe_eel_call("DisplayMessage", "Listening for voice...")
        play_assistant_sound()

        user_text = listen()
        clean_text = str(user_text or "").strip()

        if not clean_text:
            safe_eel_call("updateStatus", "Active")
            safe_eel_call("DisplayMessage", "No speech detected.")
            safe_eel_call("showToast", "No voice input detected. Please try speaking closer to microphone.", "warning")
            safe_eel_call("ShowHood")
            return {
                "success": False,
                "error": "No speech detected",
                "timestamp": timestamp_str,
            }

        safe_eel_call("updateStatus", "Processing...")
        safe_eel_call("senderText", clean_text, timestamp_str)
        safe_eel_call("setAssistantTyping", True)

        reply = process_command(clean_text, source="voice")

        safe_eel_call("setAssistantTyping", False)
        safe_eel_call("receiverText", reply, timestamp_str)
        safe_eel_call("DisplayMessage", reply[:60] + ("..." if len(reply) > 60 else ""))
        safe_eel_call("updateStatus", "Responding...")

        speak(reply, block=False)
        safe_eel_call("updateStatus", "Active")

        return {
            "success": True,
            "transcript": clean_text,
            "user_message": clean_text,
            "response": reply,
            "source": "voice",
            "timestamp": timestamp_str,
        }

    except Exception as e:
        logger.error(f"Error in voice_input: {e}")
        safe_eel_call("updateStatus", "Active")
        safe_eel_call("setAssistantTyping", False)
        error_msg = f"Voice error: {str(e)}"
        safe_eel_call("receiverText", error_msg, timestamp_str)
        return {
            "success": False,
            "error": str(e),
            "timestamp": timestamp_str,
        }
    finally:
        safe_eel_call("ShowHood")


@eel.expose
def takeAllCommands(message=None) -> dict:
    """
    Backward-compatible command processing endpoint.
    """
    if message and str(message).strip():
        return send_message(str(message), source="text")
    else:
        return voice_input()


@eel.expose
def getChatHistory(limit=25):
    """Retrieve recent conversation history for UI offcanvas."""
    try:
        return get_recent_history(limit=limit)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return []


@eel.expose
def clearChatHistory():
    """Clear conversation history."""
    try:
        clear_history()
        return True
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        return False


@eel.expose
def getSystemTelemetry():
    """Fetch system metrics for settings dialog."""
    return get_system_status()


def start() -> None:
    """Initialize Eel and start the Jarvis Assistant GUI."""
    logger.info("Initializing Jarvis Eel interface...")
    eel.init(str(config.frontend_dir))

    # Launch browser window in background
    app_url = f"http://{config.host}:{config.port}/index.html"
    launch_browser_app(app_url)

    logger.info(f"Starting Eel server on {config.host}:{config.port}...")
    eel.start(
        "index.html",
        mode=None,
        host=config.host,
        port=config.port,
        block=True,
    )


if __name__ == "__main__":
    start()