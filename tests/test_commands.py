"""
Unit tests for command processing and intent routing.
"""

from backend.command.dispatcher import process_command


def test_command_time():
    """Verify time query recognition."""
    res = process_command("what time is it?")
    assert "current time is" in res.lower()


def test_command_date():
    """Verify date query recognition."""
    res = process_command("what is today's date?")
    assert "today is" in res.lower()


def test_command_system_status():
    """Verify system diagnostics query."""
    res = process_command("system status")
    assert "system status" in res.lower()
    assert "operating system" in res.lower()


def test_command_identity():
    """Verify identity and creator query."""
    res = process_command("who are you")
    assert "jarvis" in res.lower()


def test_command_help():
    """Verify help capabilities query."""
    res = process_command("help")
    assert "capabilities" in res.lower() or "assist with" in res.lower()


def test_command_joke():
    """Verify joke generator query."""
    res = process_command("tell me a joke")
    assert len(res) > 10


def test_command_empty_input():
    """Verify handling of empty or blank inputs."""
    res = process_command("")
    assert "didn't catch that" in res.lower()

    res_space = process_command("   ")
    assert "didn't catch that" in res_space.lower()


def test_command_xss_sanitization():
    """Verify HTML script injection is stripped and safely handled."""
    res = process_command("<script>alert('hack')</script> what time is it?")
    assert "<script>" not in res
    assert "current time is" in res.lower()


def test_command_wikipedia_who_was():
    """Verify who was queries route to Wikipedia or search."""
    from unittest.mock import patch

    with patch("wikipedia.summary", return_value="Nikola Tesla was an engineer."):
        res = process_command("who was nikola tesla")
        assert "nikola tesla was an engineer" in res.lower()


def test_command_wikipedia_extract_information():
    """Verify extract information queries route to Wikipedia."""
    from unittest.mock import patch

    with patch("wikipedia.summary", return_value="Salman Khan is an Indian actor."):
        res = process_command("extract information of salman khan")
        assert "salman khan is an indian actor" in res.lower()


def test_command_wikipedia_bare():
    """Verify bare wikipedia query prompts for topic."""
    res = process_command("wikipedia")
    assert "what topic" in res.lower()

