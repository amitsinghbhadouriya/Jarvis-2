"""
Unit tests for SQLite database persistence layer.
"""

import os
import tempfile
import pytest
from backend.database import (
    init_db,
    log_command,
    get_recent_history,
    clear_history,
    add_contact,
    get_contacts,
    find_contact_by_name,
    set_setting,
    get_setting,
    add_note,
    get_notes,
    import_contacts_csv,
)


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


def test_command_history(temp_db):
    """Verify logging and retrieval of command interactions."""
    row_id = log_command("hello", "hello user", source="voice", db_path=temp_db)
    assert row_id > 0

    history = get_recent_history(limit=10, db_path=temp_db)
    assert len(history) == 1
    assert history[0]["user_input"] == "hello"
    assert history[0]["response"] == "hello user"
    assert history[0]["source"] == "voice"

    clear_history(db_path=temp_db)
    cleared = get_recent_history(limit=10, db_path=temp_db)
    assert len(cleared) == 0


def test_contacts_crud(temp_db):
    """Verify contact insertion, listing, and search."""
    cid = add_contact("Tony Stark", "+1-555-0100", "tony@stark.com", "Avenger", db_path=temp_db)
    assert cid > 0

    contacts = get_contacts(db_path=temp_db)
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Tony Stark"

    found = find_contact_by_name("Tony", db_path=temp_db)
    assert found is not None
    assert found["email"] == "tony@stark.com"

    not_found = find_contact_by_name("NonExistent", db_path=temp_db)
    assert not_found is None


def test_settings_storage(temp_db):
    """Verify settings key-value storage and overrides."""
    set_setting("volume", "85", db_path=temp_db)
    assert get_setting("volume", db_path=temp_db) == "85"

    set_setting("volume", "95", db_path=temp_db)
    assert get_setting("volume", db_path=temp_db) == "95"

    assert get_setting("non_existent", default="10", db_path=temp_db) == "10"


def test_notes_management(temp_db):
    """Verify note creation and retrieval."""
    nid = add_note("Meeting", "Discuss Stark Industries armor", db_path=temp_db)
    assert nid > 0

    notes = get_notes(db_path=temp_db)
    assert len(notes) == 1
    assert notes[0]["content"] == "Discuss Stark Industries armor"


def test_contacts_csv_import(temp_db):
    """Verify batch CSV importing of contacts."""
    fd, csv_path = tempfile.mkstemp(suffix=".csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("name,phone,email,notes\nPeter Parker,+1-555-0150,spidey@queens.ny,Spider-Man\n")
    os.close(fd)

    try:
        count = import_contacts_csv(csv_path, db_path=temp_db)
        assert count == 1
        contact = find_contact_by_name("Peter", db_path=temp_db)
        assert contact is not None
        assert contact["phone"] == "+1-555-0150"
    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)
