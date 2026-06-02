"""
Week 4 tests — simplifier and email generator.
Run from repo root: python tests/test_week4.py

NOTE: These tests make real Gemini API calls.
Make sure your .env file has GEMINI_API_KEY set before running.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.simplifier import simplify_abstract
from engine.email_generator import generate_outreach_email
from storage.email_history import save_email_draft, get_email_history

# ── Sample data ──────────────────────────────

SAMPLE_ABSTRACT = """
This project investigates energy-efficient deployment of neural networks on
resource-constrained edge devices such as microcontrollers and FPGAs.
We develop novel pruning and quantization techniques that reduce model size
by up to 90% while preserving accuracy within 2% of the original.
Applications include real-time object detection for autonomous robotics
and wearable health monitoring systems.
"""

SAMPLE_PROFILE = {
    "major": "Computer Science",
    "year": "junior",
    "interests": ["machine learning", "embedded systems", "robotics"],
    "skills": ["Python", "Rust", "C"]
}

SAMPLE_ABSTRACT_OBJ = {
    "id": "ab_test_01",
    "title": "Energy-Efficient Neural Networks for Edge Devices",
    "professor": "Dr. Jane Smith",
    "lab": "UCR Embedded AI Lab",
    "department": "CS",
    "keywords": ["ML", "embedded", "optimization"],
    "text": SAMPLE_ABSTRACT
}

# ── Simplifier Tests ─────────────────────────

def test_simplify_valid_abstract():
    result = simplify_abstract(SAMPLE_ABSTRACT)
    assert result["status"] == "success", f"Expected success, got: {result}"
    bullets = result["data"]["bullets"]
    assert len(bullets) == 3, f"Expected 3 bullets, got {len(bullets)}"
    assert any("Goal" in b for b in bullets), "Missing Goal bullet"
    assert any("Skills" in b for b in bullets), "Missing Skills bullet"
    assert any("matters" in b for b in bullets), "Missing Why it matters bullet"
    print(f"  PASS test_simplify_valid_abstract")
    for b in bullets:
        print(f"    • {b}")


def test_simplify_too_short():
    result = simplify_abstract("Too short.")
    assert result["status"] == "invalid_input", f"Expected invalid_input, got: {result}"
    print("  PASS test_simplify_too_short")


def test_simplify_empty():
    result = simplify_abstract("")
    assert result["status"] == "invalid_input", f"Expected invalid_input, got: {result}"
    print("  PASS test_simplify_empty")


# ── Email Generator Tests ────────────────────

def test_generate_email_valid():
    result = generate_outreach_email(SAMPLE_PROFILE, SAMPLE_ABSTRACT_OBJ)
    assert result["status"] == "success", f"Expected success, got: {result}"
    assert "subject" in result["data"]
    assert "body" in result["data"]
    assert len(result["data"]["subject"]) > 5
    assert len(result["data"]["body"]) > 50
    print("  PASS test_generate_email_valid")
    print(f"    Subject: {result['data']['subject']}")
    print(f"    Body preview: {result['data']['body'][:100]}...")
    return result["data"]


def test_generate_email_missing_professor():
    abstract_no_prof = {**SAMPLE_ABSTRACT_OBJ, "professor": ""}
    result = generate_outreach_email(SAMPLE_PROFILE, abstract_no_prof)
    assert result["status"] == "incomplete", f"Expected incomplete, got: {result}"
    assert "professor_name" in result["missing"]
    print("  PASS test_generate_email_missing_professor")


def test_generate_email_missing_skills():
    profile_no_skills = {**SAMPLE_PROFILE, "skills": []}
    result = generate_outreach_email(profile_no_skills, SAMPLE_ABSTRACT_OBJ)
    assert result["status"] == "incomplete", f"Expected incomplete, got: {result}"
    assert "skills" in result["missing"]
    print("  PASS test_generate_email_missing_skills")


# ── Email History Tests ──────────────────────

def test_save_and_retrieve_email_history(draft: dict):
    save_result = save_email_draft(
        "student_test01",
        "ab_test_01",
        draft["subject"],
        draft["body"]
    )
    assert save_result["status"] == "success", f"Save failed: {save_result}"
    print("  PASS test_save_email_draft")

    history_result = get_email_history("student_test01")
    assert history_result["status"] == "success", f"History fetch failed: {history_result}"
    assert len(history_result["data"]) >= 1
    assert history_result["data"][0]["subject"] == draft["subject"]
    print("  PASS test_get_email_history")


def test_history_not_found():
    result = get_email_history("student_doesnotexist")
    assert result["status"] == "not_found", f"Expected not_found, got: {result}"
    print("  PASS test_history_not_found")


# ── Run All ──────────────────────────────────

if __name__ == "__main__":
    print("\nRunning Week 4 tests...")
    print("(These make real Gemini API calls — expect a few seconds per test)\n")

    print("── Simplifier ──")
    test_simplify_valid_abstract()
    test_simplify_too_short()
    test_simplify_empty()

    print("\n── Email Generator ──")
    draft = test_generate_email_valid()
    test_generate_email_missing_professor()
    test_generate_email_missing_skills()

    print("\n── Email History ──")
    test_save_and_retrieve_email_history(draft)
    test_history_not_found()

    print("\nAll Week 4 tests passed.")