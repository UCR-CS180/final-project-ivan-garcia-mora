import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv
from engine.prompts import build_simplify_prompt

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


def simplify_abstract(abstract_text: str) -> dict:
    """
    Send a research abstract to Gemini and get back
    3 beginner-friendly bullet points.

    Returns:
        {"status": "success", "data": {"bullets": ["Goal: ...", "Skills needed: ...", "Why it matters: ..."]}}
        {"status": "invalid_input", "message": "..."}
        {"status": "engine_error", "message": "..."}
    """
    if not abstract_text or len(abstract_text.strip()) < 50:
        return {
            "status": "invalid_input",
            "message": "Abstract is too short to summarize. Minimum 50 characters required."
        }

    prompt = build_simplify_prompt(abstract_text)

    model = genai.GenerativeModel("gemini-2.5-flash")

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            parsed = _parse_gemini_json(response.text)

            bullets = parsed.get("bullets", [])
            if not bullets or len(bullets) < 3:
                return {
                    "status": "engine_error",
                    "message": "Gemini returned an incomplete summary. Try again."
                }

            return {"status": "success", "data": {"bullets": bullets}}

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