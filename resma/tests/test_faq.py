"""
Tests for engine/faq_engine.py — get_faq_response.
All Gemini calls are mocked so no API key is required.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import patch, MagicMock
from engine.faq_engine import get_faq_response


# ── Input validation ─────────────────────────────────────────────────────────

def test_faq_empty_string_returns_invalid_input():
    result = get_faq_response("")
    assert result["status"] == "invalid_input"
    assert result["message"] == "Please enter a question."


def test_faq_whitespace_only_returns_invalid_input():
    result = get_faq_response("   ")
    assert result["status"] == "invalid_input"
    assert result["message"] == "Please enter a question."


# ── Success path ─────────────────────────────────────────────────────────────

def test_faq_valid_question_returns_answer():
    mock_response = MagicMock()
    mock_response.text = '{"found": true, "answer": "Create a profile, then go to Find Matches."}'

    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.return_value = mock_response
        result = get_faq_response("How do I find research matches?")

    assert result["status"] == "success"
    assert result["data"]["answer"] == "Create a profile, then go to Find Matches."


def test_faq_strips_markdown_fences_before_parsing():
    """Gemini sometimes wraps JSON in ```json fences — _parse_gemini_json must strip them."""
    mock_response = MagicMock()
    mock_response.text = '```json\n{"found": true, "answer": "Enter your student ID."}\n```'

    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.return_value = mock_response
        result = get_faq_response("How do I use the app?")

    assert result["status"] == "success"
    assert result["data"]["answer"] == "Enter your student ID."


# ── Not-found path ───────────────────────────────────────────────────────────

def test_faq_off_topic_question_returns_not_found():
    mock_response = MagicMock()
    mock_response.text = '{"found": false, "answer": ""}'

    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.return_value = mock_response
        result = get_faq_response("What is the weather in Riverside?")

    assert result["status"] == "not_found"
    assert result["message"] == "I don't have that information yet."


# ── Error paths ──────────────────────────────────────────────────────────────

def test_faq_unparseable_response_returns_engine_error():
    mock_response = MagicMock()
    mock_response.text = "this is not json"

    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.return_value = mock_response
        result = get_faq_response("What is ResMAI?")

    assert result["status"] == "engine_error"


def test_faq_503_exhausts_retries_and_returns_engine_error():
    """All three retry attempts fail with 503 — should return engine_error, not raise."""
    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.side_effect = Exception("503 UNAVAILABLE: high demand")
        with patch("engine.faq_engine.time.sleep"):
            result = get_faq_response("How does matching work?")

    assert result["status"] == "engine_error"
    assert "503" in result["message"] or "UNAVAILABLE" in result["message"]


def test_faq_non_503_exception_returns_engine_error_immediately():
    """A non-503 exception should not retry — fail on the first attempt."""
    call_count = 0

    def raise_once(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise Exception("some unexpected error")

    with patch("engine.faq_engine.genai.GenerativeModel") as mock_cls:
        mock_cls.return_value.generate_content.side_effect = raise_once
        result = get_faq_response("Tell me about the lab.")

    assert result["status"] == "engine_error"
    assert call_count == 1
