"""
Web searching, browser launching, and Wikipedia lookup handler.
"""

import re
import urllib.parse
import webbrowser
from typing import Optional
from backend.logger import get_logger

logger = get_logger("SearchHandler")


def handle_web_search(query: str) -> Optional[str]:
    """Execute search on Google."""
    cleaned = re.sub(r"^(search\s+for|search|google|find)\s+", "", query, flags=re.IGNORECASE).strip()
    if not cleaned:
        return "What would you like me to search for?"

    encoded = urllib.parse.quote_plus(cleaned)
    url = f"https://www.google.com/search?q={encoded}"
    try:
        webbrowser.open(url)
        return f"Searching Google for '{cleaned}'."
    except Exception as e:
        logger.error(f"Failed to open browser search: {e}")
        return f"Failed to open browser for '{cleaned}'."


def handle_youtube(query: str) -> Optional[str]:
    """Search or open YouTube."""
    cleaned = re.sub(
        r"^(open\s+youtube|play\s+on\s+youtube|youtube\s+search|search\s+youtube\s+for|play)\s*",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(r"\s+on\s+youtube$", "", cleaned, flags=re.IGNORECASE).strip()

    if not cleaned:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    encoded = urllib.parse.quote_plus(cleaned)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    return f"Searching YouTube for '{cleaned}'."


def handle_wikipedia(query: str) -> Optional[str]:
    """Fetch concise summary from Wikipedia if available."""
    cleaned = re.sub(
        r"^(wikipedia|who\s+is|what\s+is|tell\s+me\s+about)\s+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()
    if not cleaned:
        return "What topic would you like me to look up?"

    try:
        import wikipedia

        wikipedia.set_lang("en")
        summary = wikipedia.summary(cleaned, sentences=2)
        return f"According to Wikipedia: {summary}"
    except Exception as e:
        logger.debug(f"Wikipedia lookup notice for '{cleaned}': {e}")
        # Fallback to web search
        return handle_web_search(cleaned)


def handle_open_site(query: str) -> Optional[str]:
    """Open common domains directly in browser."""
    sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://www.x.com",
        "x": "https://www.x.com",
        "linkedin": "https://www.linkedin.com",
        "gmail": "https://mail.google.com",
    }
    for site_key, url in sites.items():
        if f"open {site_key}" in query.lower() or query.lower() == site_key:
            webbrowser.open(url)
            return f"Opening {site_key.capitalize()}."
    return None
