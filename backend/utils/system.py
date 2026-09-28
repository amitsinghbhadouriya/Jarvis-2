"""
System utilities and hardware telemetry for Jarvis 2.
"""

import os
import re
import sys
import html
import platform
import subprocess
from typing import Dict, Any
from backend.logger import get_logger

logger = get_logger("SystemUtils")


def sanitize_input(text: str) -> str:
    """
    Sanitize text input by removing control characters, trimming whitespace,
    and stripping potentially malicious script blocks and HTML tags.
    """
    if not text:
        return ""
    # Strip invisible control chars except newlines and tabs
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Remove script and style blocks entirely along with their inner code
    clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", clean, flags=re.DOTALL | re.IGNORECASE)
    # Remove remaining HTML tags
    clean = re.sub(r"<[^>]+>", "", clean)
    return clean.strip()



def escape_html(text: str) -> str:
    """Escape HTML entities for safe browser presentation."""
    return html.escape(text or "")


def get_system_status() -> Dict[str, Any]:
    """Retrieve operational telemetry about the host system."""
    status: Dict[str, Any] = {
        "os": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "battery": "Unknown",
        "power_plugged": None,
    }

    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            status["battery"] = f"{int(battery.percent)}%"
            status["power_plugged"] = battery.power_plugged
        status["cpu_percent"] = f"{psutil.cpu_percent(interval=None)}%"
        status["memory_percent"] = f"{psutil.virtual_memory().percent}%"
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"Failed to query battery/CPU telemetry: {e}")

    return status


def launch_application(target: str) -> bool:
    """
    Safely launch an application or command without shell injection vulnerability.
    """
    known_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "cmd": "cmd.exe",
        "explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "taskmgr": "taskmgr.exe",
    }

    executable = known_apps.get(target.lower(), target)
    try:
        if sys.platform == "win32":
            subprocess.Popen([executable], shell=False)
        else:
            subprocess.Popen([executable])
        logger.info(f"Launched application: {executable}")
        return True
    except Exception as e:
        logger.error(f"Failed to launch application '{executable}': {e}")
        return False
