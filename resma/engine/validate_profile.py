def validate_profile(raw_input: dict) -> dict:
    """
    Validate and normalize a raw student profile input.

    Expected fields:
        email, major, year, interests (str or list), skills (str or list)

    Returns:
        {"status": "success", "data": {...normalized profile...}}
        {"status": "incomplete", "missing": [...]}
        {"status": "validation_error", "message": "..."}
    """

    required = ["email", "major", "year", "interests", "skills"]
    missing = [f for f in required if not raw_input.get(f)]

    if missing:
        return {"status": "incomplete", "missing": missing}

    valid_years = ["freshman", "sophomore", "junior", "senior"]
    year = raw_input["year"].strip().lower()

    if year not in valid_years:
        return {
            "status": "validation_error",
            "message": f"Invalid year '{raw_input['year']}'. Must be one of: {', '.join(valid_years)}"
        }

    # normalize interests — accept comma string or list
    interests = raw_input["interests"]
    if isinstance(interests, str):
        interests = [i.strip().lower() for i in interests.split(",") if i.strip()]
    else:
        interests = [i.strip().lower() for i in interests if i.strip()]

    if not interests:
        return {"status": "incomplete", "missing": ["interests"]}

    # normalize skills — accept comma string or list
    skills = raw_input["skills"]
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    else:
        skills = [s.strip() for s in skills if s.strip()]

    if not skills:
        return {"status": "incomplete", "missing": ["skills"]}

    # normalize email
    email = raw_input["email"].strip().lower()
    if "@" not in email:
        return {"status": "validation_error", "message": "Invalid email address"}

    return {
        "status": "success",
        "data": {
            "email": email,
            "major": raw_input["major"].strip(),
            "year": year,
            "interests": interests,
            "skills": skills
        }
    }