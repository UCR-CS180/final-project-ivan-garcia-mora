"""
Week 3 tests — Gemini matching flow.
Run from repo root: python tests/test_matching.py

NOTE: These tests make real Gemini API calls.
Make sure your .env file has GEMINI_API_KEY set before running.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.profile_service import submit_profile, fetch_profile_by_email
from engine.matching_service import run_matching, refresh_matches
from storage.profiles import delete_profile
from storage.match_cache import get_cached_matches, clear_cache

TEST_EMAIL = "testweek3@ucr.edu"


def cleanup():
    result = fetch_profile_by_email(TEST_EMAIL)
    if result["status"] == "success":
        pid = result["data"]["id"]
        clear_cache(pid)
        delete_profile(pid)


def setup_test_profile() -> str:
    cleanup()
    result = submit_profile({
        "email": TEST_EMAIL,
        "major": "Computer Science",
        "year": "junior",
        "interests": "machine learning, embedded systems, robotics",
        "skills": "Python, Rust, C"
    })
    assert result["status"] == "success", f"Profile setup failed: {result}"
    return result["id"]


def test_matching_returns_results(profile_id: str):
    result = run_matching(profile_id, use_cache=False)
    assert result["status"] == "success", f"Expected success, got: {result}"
    assert "matches" in result["data"]
    assert len(result["data"]["matches"]) >= 1

    match = result["data"]["matches"][0]
    assert "abstract_id" in match
    assert "rank" in match
    assert "reason" in match
    assert isinstance(match["reason"], str)
    assert len(match["reason"]) > 5

    print(f"  PASS test_matching_returns_results — {len(result['data']['matches'])} matches found")
    return result["data"]["matches"]


def test_cache_is_saved(profile_id: str):
    # cache should exist after previous test ran matching
    cached = get_cached_matches(profile_id)
    assert cached["status"] == "success", f"Expected cached results, got: {cached}"
    assert len(cached["data"]["matches"]) >= 1
    print("  PASS test_cache_is_saved")


def test_cache_is_used(profile_id: str):
    result = run_matching(profile_id, use_cache=True)
    assert result["status"] == "success"
    assert result["data"]["from_cache"] == True
    print("  PASS test_cache_is_used — cache hit confirmed")


def test_refresh_bypasses_cache(profile_id: str):
    result = refresh_matches(profile_id)
    assert result["status"] == "success"
    assert result["data"]["from_cache"] == False
    print("  PASS test_refresh_bypasses_cache — fresh Gemini call confirmed")


def test_not_found():
    result = run_matching("student_doesnotexist")
    assert result["status"] == "not_found", f"Expected not_found, got: {result}"
    print("  PASS test_not_found")


if __name__ == "__main__":
    print("\nRunning Week 3 matching flow tests...")
    print("(These make real Gemini API calls — expect a few seconds per test)\n")

    profile_id = setup_test_profile()
    print(f"Test profile created: {profile_id}\n")

    test_matching_returns_results(profile_id)
    test_cache_is_saved(profile_id)
    test_cache_is_used(profile_id)
    test_refresh_bypasses_cache(profile_id)
    test_not_found()

    cleanup()
    print("\nAll tests passed. Database cleaned up.")