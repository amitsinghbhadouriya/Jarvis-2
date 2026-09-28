"""
Contacts and address book query handler.
"""

import re
from typing import Optional
from backend.database import get_contacts, find_contact_by_name


def handle_contacts(query: str) -> Optional[str]:
    """Search for contact details by name."""
    match = re.search(r"(?:find|search|lookup|get)\s+contact\s+([a-zA-Z\s]+)", query, re.IGNORECASE)
    if not match:
        if "contacts" in query.lower() or "address book" in query.lower():
            all_contacts = get_contacts()
            if not all_contacts:
                return "Your contacts list is currently empty. You can add entries or import contacts.csv."
            names = [f"- {c['name']} ({c['phone'] or c['email'] or 'No details'})" for c in all_contacts[:10]]
            return "Contacts directory:\n" + "\n".join(names)
        return None

    name = match.group(1).strip()
    contact = find_contact_by_name(name)
    if contact:
        details = [f"Name: {contact['name']}"]
        if contact.get("phone"):
            details.append(f"Phone: {contact['phone']}")
        if contact.get("email"):
            details.append(f"Email: {contact['email']}")
        if contact.get("notes"):
            details.append(f"Notes: {contact['notes']}")
        return "Contact Found:\n" + "\n".join(details)
    return f"No contact found matching '{name}' in your address book."
