"""
System command handler for time, date, battery, and diagnostic status.
"""

import datetime
from typing import Optional
from backend.utils.system import get_system_status


def handle_time(query: str) -> Optional[str]:
    """Provide current local time."""
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def handle_date(query: str) -> Optional[str]:
    """Provide current date and day."""
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."


def handle_system_status(query: str) -> Optional[str]:
    """Provide system telemetry status."""
    status = get_system_status()
    os_name = status.get("os", "System")
    battery = status.get("battery", "Unknown")
    cpu = status.get("cpu_percent", "N/A")
    mem = status.get("memory_percent", "N/A")

    details = [f"Operating System: {os_name}"]
    if battery != "Unknown":
        plugged = "Charging" if status.get("power_plugged") else "On Battery"
        details.append(f"Battery: {battery} ({plugged})")
    if cpu != "N/A":
        details.append(f"CPU Utilization: {cpu}")
    if mem != "N/A":
        details.append(f"Memory Usage: {mem}")

    return "System Status:\n" + "\n".join(f"- {d}" for d in details)
