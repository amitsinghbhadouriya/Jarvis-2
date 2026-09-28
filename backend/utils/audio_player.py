"""
Asynchronous and synchronous audio file playback utility.
"""

import os
import sys
import threading
from pathlib import Path
from typing import Union
from backend.logger import get_logger

logger = get_logger("AudioPlayer")


def play_sound_file(file_path: Union[str, Path], async_play: bool = True) -> bool:
    """
    Play a WAV sound file asynchronously or synchronously.
    Uses native winsound on Windows for optimal low-latency playback.
    """
    path_str = str(file_path)
    if not os.path.exists(path_str):
        logger.warning(f"Audio file not found: {path_str}")
        return False

    try:
        if sys.platform == "win32":
            import winsound

            flags = winsound.SND_FILENAME
            if async_play:
                flags |= winsound.SND_ASYNC
            winsound.PlaySound(path_str, flags)
            return True
        else:
            # Unix / macOS fallback via a background thread
            def _play_posix():
                try:
                    import subprocess
                    subprocess.run(["aplay", path_str], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

            if async_play:
                threading.Thread(target=_play_posix, daemon=True).start()
            else:
                _play_posix()
            return True

    except Exception as e:
        logger.error(f"Failed to play audio file '{path_str}': {e}")
        return False
