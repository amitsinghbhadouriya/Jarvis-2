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


def start() -> None:
    """Initialize Eel and start the Jarvis Assistant GUI."""
    logger.info("Initializing Jarvis Eel interface...")
    eel.init(str(config.frontend_dir))

    # Expose audio playback to Eel
    @eel.expose
    def play_assistant_sound_effect():
        play_assistant_sound()

    @eel.expose
    def init():
        """Initialize GUI after page load and execute face authentication."""
        try:
            logger.info("Starting authentication flow...")
            eel.hideLoader()
            speak("Welcome to Jarvis. Initiating facial authentication.")

            flag = authenticate_face()
            if flag == 1:
                speak("Face recognized successfully.")
                play_success_sound()
                time.sleep(0.8)
                eel.hideFaceAuth()
                time.sleep(0.5)
                eel.hideFaceAuthSuccess()
                time.sleep(1.0)
                speak("Welcome back. Jarvis online and awaiting commands.")
                eel.hideStart()
                play_assistant_sound()
            else:
                speak("Authentication failed. Please verify camera positioning.")
                play_error_sound()
                # Allow fallback after warning
                time.sleep(1.0)
                eel.hideFaceAuth()
                eel.hideStart()
        except Exception as e:
            logger.error(f"Error during init flow: {e}")
            eel.hideLoader()
            eel.hideStart()

    @eel.expose
    def takeAllCommands(message=None):
        """
        Process voice input or typed message from the chatbox.
        Dispatches to command engine and returns synthesized speech & UI response.
        """
        try:
            user_text = message
            source = "text"

            if not user_text or not str(user_text).strip():
                # Trigger voice input
                source = "voice"
                eel.DisplayMessage("Listening...")
                user_text = listen()

            clean_text = str(user_text or "").strip()
            if not clean_text:
                eel.ShowHood()
                return

            # Display user speech/text in chat history
            eel.senderText(clean_text)

            # Process query
            reply = process_command(clean_text, source=source)

            # Display bot response and speak
            eel.receiverText(reply)
            eel.DisplayMessage(reply[:50] + ("..." if len(reply) > 50 else ""))
            speak(reply, block=False)

        except Exception as e:
            logger.error(f"Exception in takeAllCommands: {e}")
            error_msg = f"Error: {str(e)}"
            eel.receiverText(error_msg)
        finally:
            eel.ShowHood()

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