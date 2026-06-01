from storage.profiles import get_profile
from storage.abstracts import get_abstracts
from storage.match_cache import save_matches, get_cached_matches, clear_cache
from engine.match_engine import call_gemini_match


def run_matching(profile_id: str, use_cache: bool = True) -> dict:
    """
    Full matching pipeline:
    1. Load student profile from storage
    2. Check cache — return early if results already exist
    3. Load all abstracts from storage
    4. Call Gemini to rank matches
    5. Cache results and return

    Args:
        profile_id: the student's ID
        use_cache: set False to force a fresh Gemini call

    Returns:
        {"status": "success", "data": {"matches": [...], "from_cache": bool}}
        {"status": "not_found"}
        {"status": "no_abstracts"}
        {"status": "no_matches", "message": "..."}
        {"status": "engine_error", "message": "..."}
        {"status": "db_error", "message": "..."}
    """
    # step 1: load profile
    profile_result = get_profile(profile_id)
    if profile_result["status"] != "success":
        return profile_result

    profile = profile_result["data"]

    # step 2: check cache
    if use_cache:
        cached = get_cached_matches(profile_id)
        if cached["status"] == "success":
            cached["data"]["from_cache"] = True
            return cached

    # step 3: load abstracts
    abstracts_result = get_abstracts()
    if abstracts_result["status"] != "success":
        return abstracts_result

    abstracts = abstracts_result["data"]

    # step 4: call Gemini
    match_result = call_gemini_match(profile, abstracts)
    if match_result["status"] != "success":
        return match_result

    matches = match_result["data"]["matches"]

    # step 5: cache results
    save_matches(profile_id, matches)

    return {
        "status": "success",
        "data": {
            "matches": matches,
            "from_cache": False
        }
    }


def refresh_matches(profile_id: str) -> dict:
    """
    Force a fresh Gemini call by clearing the cache first.
    Use this when a student updates their profile.

    Returns same payloads as run_matching.
    """
    clear_cache(profile_id)
    return run_matching(profile_id, use_cache=False)