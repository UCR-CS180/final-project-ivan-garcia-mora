import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from engine.prompts import build_email_prompt

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _parse_gemini_json(raw_text: str) -> dict:
    """Strip markdown fences and parse JSON from Gemini response."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return json.loads(text)


def generate_outreach_email(profile: dict, abstract: dict) -> dict:
    """
    Generate a professional outreach email from a student
    to a professor based on their profile and a research abstract.

    Returns:
        {"status": "success", "data": {"subject": "...", "body": "..."}}
        {"status": "incomplete", "missing": [...]}
        {"status": "engine_error", "message": "..."}
    """
    # check required fields
    missing = []
    if not profile.get("major"):
        missing.append("major")
    if not profile.get("skills"):
        missing.append("skills")
    if not abstract.get("title"):
        missing.append("abstract title")
    if not abstract.get("professor"):
        missing.append("professor_name")

    if missing:
        return {"status": "incomplete", "missing": missing}

    prompt = build_email_prompt(profile, abstract)

    model = genai.GenerativeModel("gemini-2.5-flash")

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            parsed = _parse_gemini_json(response.text)

            subject = parsed.get("subject", "")
            body = parsed.get("body", "")

            if not subject or not body:
                return {
                    "status": "engine_error",
                    "message": "Gemini returned an incomplete email. Try again."
                }

            return {"status": "success", "data": {"subject": subject, "body": body}}

        except json.JSONDecodeError:
            return {
                "status": "engine_error",
                "message": "Gemini returned an unparseable response. Try again."
            }
        except Exception as e:
            if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e)):
                time.sleep(3 * (attempt + 1))
                continue
            return {"status": "engine_error", "message": str(e)}