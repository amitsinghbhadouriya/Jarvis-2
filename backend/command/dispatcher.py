"""
Command Dispatcher and Intent Router for Jarvis 2.
Evaluates user input against registered domain handlers.
"""

from typing import Optional
from backend.logger import get_logger
from backend.database import log_command
from backend.utils.system import sanitize_input
from backend.command.handlers.system_handler import (
    handle_time,
    handle_date,
    handle_system_status,
)
from backend.command.handlers.search_handler import (
    handle_web_search,
    handle_youtube,
    handle_wikipedia,
    handle_open_site,
)
from backend.command.handlers.app_handler import handle_open_app
from backend.command.handlers.contacts_handler import handle_contacts
from backend.command.handlers.notes_handler import handle_notes
from backend.command.handlers.conversation_handler import (
    handle_greeting,
    handle_identity,
    handle_help,
    handle_joke,
)

logger = get_logger("Dispatcher")


def process_command(user_input: Optional[str], source: str = "voice") -> str:
    """
    Parse and execute a user command, returning the assistant response string.
    Automatically records the transaction in database history.
    """
    if not user_input or not user_input.strip():
        return "I didn't catch that. Please try speaking or typing again."

    query = sanitize_input(user_input).strip()
    lowered = query.lower()
    logger.info(f"Dispatching query: '{query}' (source: {source})")

    try:
        response: Optional[str] = None

        # 1. System Time & Date
        if any(w in lowered for w in ["what time", "current time", "the time"]) or lowered == "time":
            response = handle_time(query)
        elif any(w in lowered for w in ["what date", "today's date", "which day", "current date"]) or lowered == "date":
            response = handle_date(query)
        elif any(w in lowered for w in ["system status", "battery", "system health", "diagnostics"]):
            response = handle_system_status(query)

        # 2. Local Applications
        elif lowered.startswith(("open ", "launch ", "start ")):
            # Check site first, then local app
            response = handle_open_site(query) or handle_open_app(query)

        # 3. Media & Search
        elif any(w in lowered for w in ["youtube", "play on youtube", "play"]):
            response = handle_youtube(query)
        elif any(w in lowered for w in ["wikipedia", "who is", "what is", "tell me about"]):
            response = handle_wikipedia(query)
        elif lowered.startswith(("search for", "search", "google", "find")):
            response = handle_web_search(query)

        # 4. Contacts & Notes
        elif "contact" in lowered:
            response = handle_contacts(query)
        elif any(w in lowered for w in ["note", "memo"]):
            response = handle_notes(query)

        # 5. Conversational Intents
        elif any(w in lowered for w in ["hello", "hi", "hey", "good morning", "good evening"]):
            response = handle_greeting(query)
        elif any(w in lowered for w in ["who are you", "what is your name", "your name"]):
            response = handle_identity(query)
        elif any(w in lowered for w in ["help", "what can you do", "capabilities", "features"]):
            response = handle_help(query)
        elif any(w in lowered for w in ["joke", "make me laugh"]):
            response = handle_joke(query)

        # 6. Fallback Response
        if not response:
            response = (
                f"I processed your command: '{query}'. "
                "I can assist with time, date, web search, system diagnostics, notes, and launching apps. "
                "Say 'Help' for a list of capabilities."
            )

        # Record to database
        try:
            log_command(user_input=query, response=response, source=source)
        except Exception as db_err:
            logger.warning(f"Failed to record command in database: {db_err}")

        return response

    except Exception as e:
        logger.error(f"Error processing command '{query}': {e}")
        return f"An error occurred while processing your request: {str(e)}"
