"""
Quick notes and memo query handler.
"""

import re
from typing import Optional
from backend.database import add_note, get_notes


def handle_notes(query: str) -> Optional[str]:
    """Create or list quick notes."""
    # Create note: "take note ...", "create note ...", "note down ..."
    match_add = re.search(r"(?:take\s+note|create\s+note|note\s+down|write\s+note)\s+(.+)", query, re.IGNORECASE)
    if match_add:
        content = match_add.group(1).strip()
        add_note(title="Quick Note", content=content)
        return f"Note recorded: '{content}'"

    # List notes: "show notes", "read notes", "my notes"
    if any(k in query.lower() for k in ["show notes", "read notes", "my notes", "list notes"]):
        notes = get_notes()
        if not notes:
            return "You have no saved notes."
        summary = [f"{i+1}. {n['content']} ({n['created_at'][:10]})" for i, n in enumerate(notes[:5])]
        return "Recent Notes:\n" + "\n".join(summary)

    return None
