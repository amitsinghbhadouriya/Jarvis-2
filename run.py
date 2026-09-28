"""
Jarvis 2 - Multi-Process Orchestrator
Supervises GUI process and background hotword recognition daemon.
"""

import sys
import signal
import multiprocessing
from backend.logger import get_logger

logger = get_logger("Launcher")


def start_jarvis():
    """Start the main Eel interface and backend server."""
    logger.info("Initializing Assistant GUI process...")
    try:
        from main import start
        start()
    except Exception as e:
        logger.error(f"Error in Jarvis GUI process: {e}")


def listen_hotword():
    """Start continuous hotword detection daemon."""
    logger.info("Initializing wake-word detection daemon...")
    try:
        from backend.feature import hotword
        hotword()
    except Exception as e:
        logger.error(f"Error in hotword daemon: {e}")


def main():
    """Supervise child processes with graceful termination."""
    multiprocessing.freeze_support()

    logger.info("Starting Jarvis 2 dual-process system...")

    process_gui = multiprocessing.Process(target=start_jarvis, name="JarvisGUI")
    process_hotword = multiprocessing.Process(target=listen_hotword, name="JarvisHotword", daemon=True)

    def sigint_handler(signum, frame):
        logger.info("Received interrupt signal. Gracefully shutting down...")
        if process_gui.is_alive():
            process_gui.terminate()
        if process_hotword.is_alive():
            process_hotword.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    process_gui.start()
    process_hotword.start()

    # Wait for GUI to close
    process_gui.join()

    # Cleanly terminate hotword daemon after GUI closes
    if process_hotword.is_alive():
        logger.info("GUI closed. Terminating hotword process...")
        process_hotword.terminate()
        process_hotword.join(timeout=2.0)

    logger.info("Jarvis 2 system terminated cleanly.")


if __name__ == "__main__":
    main()