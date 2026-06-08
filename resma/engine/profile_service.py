from engine.validate_profile import validate_profile
from storage.profiles import save_profile, get_profile, get_profile_by_email


def submit_profile(raw_input: dict) -> dict:
    """
    Validate and save a new student profile.

    Args:
        raw_input (dict): Raw form fields — email (str), major (str),
            year (str), interests (str), skills (str).

    Returns:
        {"status": "success", "id": "student_xxx"}
        {"status": "incomplete", "missing": [...]}
        {"status": "validation_error", "message": "..."}
        {"status": "exists", "message": "..."}
        {"status": "db_error", "message": "..."}
    """
    # step 1: validate
    validation_result = validate_profile(raw_input)
    if validation_result["status"] != "success":
        return validation_result

    # step 2: save
    return save_profile(validation_result["data"])


def fetch_profile(profile_id: str) -> dict:
    """
    Retrieve a student profile by ID.

    Returns:
        {"status": "success", "data": {...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    return get_profile(profile_id)


def fetch_profile_by_email(email: str) -> dict:
    """
    Retrieve a student profile by email.
    Useful for returning users who forgot their student ID.

    Returns:
        {"status": "success", "data": {...}}
        {"status": "not_found"}
        {"status": "db_error", "message": "..."}
    """
    return get_profile_by_email(email)