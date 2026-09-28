"""
Conversational and small-talk intent handler.
"""

import random
from typing import Optional


JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the AI go to school? To improve its neural networks!",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Hardware is the part of a computer that you can kick; software is the part that you can only curse at.",
]

GREETINGS = [
    "Hello! How can I assist you today?",
    "Greetings! I am online and ready for your commands.",
    "Hi there! What can I do for you today?",
    "At your service. How may I assist you?",
]


def handle_greeting(query: str) -> Optional[str]:
    """Handle conversational greetings."""
    return random.choice(GREETINGS)


def handle_identity(query: str) -> Optional[str]:
    """Respond with assistant identity."""
    return "I am JARVIS, your intelligent desktop assistant, inspired by Stark Industries architecture."


def handle_help(query: str) -> Optional[str]:
    """Provide summary of capabilities."""
    return (
        "Here are a few things I can assist with:\n"
        "- Time & Date: 'What time is it?', 'What is today's date?'\n"
        "- System Telemetry: 'Check system status', 'Battery level'\n"
        "- Web & Media: 'Search Google for quantum computing', 'Play AC/DC on YouTube'\n"
        "- Wikipedia: 'Who was Nikola Tesla?'\n"
        "- App Launcher: 'Open Notepad', 'Open Calculator'\n"
        "- Contacts: 'Find contact Tony'\n"
        "- Notes: 'Create note Meeting notes'\n"
        "- Humor: 'Tell me a joke'"
    )


def handle_joke(query: str) -> Optional[str]:
    """Tell a programming or AI joke."""
    return random.choice(JOKES)
