"""
Local desktop application launcher handler.
"""

import re
from typing import Optional
from backend.utils.system import launch_application


def handle_open_app(query: str) -> Optional[str]:
    """Inspect query and launch requested desktop application."""
    match = re.search(r"^(?:open|launch|start)\s+([a-zA-Z0-9_\-\s]+)$", query.strip(), re.IGNORECASE)
    if not match:
        return None

    app_target = match.group(1).strip().lower()
    app_aliases = {
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "cmd": "cmd",
        "terminal": "cmd",
        "command prompt": "cmd",
        "file explorer": "explorer",
        "explorer": "explorer",
        "paint": "mspaint",
        "task manager": "taskmgr",
    }

    if app_target in app_aliases:
        success = launch_application(app_aliases[app_target])
        if success:
            return f"Opening {app_target.title()}."
        return f"Could not launch {app_target.title()} on this system."

    return None
