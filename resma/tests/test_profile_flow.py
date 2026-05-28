"""
Week 2 tests — profile submission flow.
Run from repo root: python tests/test_profile_flow.py
"""

from engine.profile_service import submit_profile, fetch_profile, fetch_profile_by_email
from storage.profiles import delete_profile

TEST_EMAIL = "testweek2@ucr.edu"


def cleanup():
    result = fetch_profile_by_email(TEST_EMAIL)
    if result["status"] == "success":
        delete_profile(result["data"]["id"])


def test_valid_profile():
    cleanup()
    result = submit_profile({
        "email": TEST_EMAIL,
        "major": "CS",
        "year": "junior",
        "interests": "machine learning, robotics",
        "skills": "Python, Rust"
    })
    assert result["status"] == "success", f"Expected success, got: {result}"
    assert result["id"].startswith("student_")
    print(f"  PASS test_valid_profile — id: {result['id']}")
    return result["id"]


def test_duplicate_email():
    result = submit_profile({
        "email": TEST_EMAIL,
        "major": "CS",
        "year": "junior",
        "interests": "ML",
        "skills": "Python"
    })
    assert result["status"] == "exists", f"Expected exists, got: {result}"
    print("  PASS test_duplicate_email")


def test_missing_field():
    result = submit_profile({
        "email": "missing@ucr.edu",
        "major": "",
        "year": "junior",
        "interests": "ML",
        "skills": "Python"
    })
    assert result["status"] == "incomplete", f"Expected incomplete, got: {result}"
    assert "major" in result["missing"]
    print("  PASS test_missing_field")


def test_invalid_year():
    result = submit_profile({
        "email": "badyear@ucr.edu",
        "major": "CS",
        "year": "grad",
        "interests": "ML",
        "skills": "Python"
    })
    assert result["status"] == "validation_error", f"Expected validation_error, got: {result}"
    print("  PASS test_invalid_year")


def test_invalid_email():
    result = submit_profile({
        "email": "notanemail",
        "major": "CS",
        "year": "junior",
        "interests": "ML",
        "skills": "Python"
    })
    assert result["status"] == "validation_error", f"Expected validation_error, got: {result}"
    print("  PASS test_invalid_email")


def test_fetch_profile(profile_id: str):
    result = fetch_profile(profile_id)
    assert result["status"] == "success", f"Expected success, got: {result}"
    assert result["data"]["major"] == "CS"
    assert isinstance(result["data"]["interests"], list)
    assert isinstance(result["data"]["skills"], list)
    print("  PASS test_fetch_profile")


def test_fetch_by_email():
    result = fetch_profile_by_email(TEST_EMAIL)
    assert result["status"] == "success", f"Expected success, got: {result}"
    assert result["data"]["email"] == TEST_EMAIL
    print("  PASS test_fetch_by_email")


def test_fetch_not_found():
    result = fetch_profile("student_doesnotexist")
    assert result["status"] == "not_found", f"Expected not_found, got: {result}"
    print("  PASS test_fetch_not_found")


if __name__ == "__main__":
    print("\nRunning Week 2 profile flow tests...\n")

    profile_id = test_valid_profile()
    test_duplicate_email()
    test_missing_field()
    test_invalid_year()
    test_invalid_email()
    test_fetch_profile(profile_id)
    test_fetch_by_email()
    test_fetch_not_found()

    cleanup()
    print("\nAll tests passed. Database cleaned up.")