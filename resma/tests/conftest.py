import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.profile_service import submit_profile, fetch_profile_by_email
from storage.profiles import delete_profile
from storage.match_cache import clear_cache

_FIXTURE_EMAIL = "testfixture@ucr.edu"


@pytest.fixture(scope="session")
def profile_id():
    """Create a real student profile for the session and clean up after."""
    existing = fetch_profile_by_email(_FIXTURE_EMAIL)
    if existing["status"] == "success":
        pid = existing["data"]["id"]
        clear_cache(pid)
        delete_profile(pid)

    result = submit_profile({
        "email": _FIXTURE_EMAIL,
        "major": "CS",
        "year": "junior",
        "interests": "machine learning, robotics",
        "skills": "Python, Rust",
    })
    assert result["status"] == "success", f"Fixture profile setup failed: {result}"
    pid = result["id"]

    yield pid

    clear_cache(pid)
    delete_profile(pid)


@pytest.fixture
def draft():
    """Return a minimal email draft dict without making a real Gemini call."""
    return {
        "subject": "Interest in Research Opportunity",
        "body": "Dear Professor, I am very interested in your research on edge AI.",
    }
