import json
import os
from dotenv import load_dotenv
from google import genai
from engine.prompts import build_match_prompt

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = "gemini-2.5-flash"


def _parse_gemini_json(raw_text: str) -> dict:
    """
    Safely parse Gemini's response, stripping markdown fences if present.
    Returns parsed dict or raises ValueError.
    """
    text = raw_text.strip()

    # strip ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        lines = text.split("\n")
        # remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    return json.loads(text)


def call_gemini_match(profile: dict, abstracts: list) -> dict:
    """
    Send student profile + abstracts to Gemini.
    Returns ranked match list or error payload.

    Returns:
        {"status": "success", "data": {"matches": [...]}}
        {"status": "no_abstracts"}
        {"status": "no_matches", "message": "..."}
        {"status": "engine_error", "message": "..."}
    """
    if not abstracts:
        return {"status": "no_abstracts"}

    prompt = build_match_prompt(profile, abstracts)

    try:
        response = _client.models.generate_content(model=_MODEL, contents=prompt)
        raw_text = response.text

        parsed = _parse_gemini_json(raw_text)
        matches = parsed.get("matches", [])

        if not matches:
            return {
                "status": "no_matches",
                "message": "No relevant matches found. Try broadening your interests."
            }

        return {"status": "success", "data": {"matches": matches}}

    except json.JSONDecodeError:
        return {
            "status": "engine_error",
            "message": "Gemini returned an unparseable response. Try again."
        }
    except Exception as e:
        return {"status": "engine_error", "message": str(e)}