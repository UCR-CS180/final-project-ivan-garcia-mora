import json
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from engine.prompts import build_faq_prompt

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _parse_gemini_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return json.loads(text)


def get_faq_response(user_query: str) -> dict:
    """
    Answer a student FAQ question about ResMAI or UCR undergraduate research.

    Args:
        user_query (str): The student's free-text question.

    Returns:
        {"status": "success", "data": {"answer": "..."}}
        {"status": "not_found", "message": "I don't have that information yet."}
        {"status": "invalid_input", "message": "Please enter a question."}
        {"status": "engine_error", "message": "..."}
    """
    if not user_query or not user_query.strip():
        return {"status": "invalid_input", "message": "Please enter a question."}

    prompt = build_faq_prompt(user_query.strip())
    model = genai.GenerativeModel("gemini-2.5-flash")

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            parsed = _parse_gemini_json(response.text)

            if not parsed.get("found"):
                return {
                    "status": "not_found",
                    "message": "I don't have that information yet."
                }

            return {"status": "success", "data": {"answer": parsed["answer"]}}

        except json.JSONDecodeError:
            return {"status": "engine_error", "message": "Unexpected response from AI. Try again."}
        except Exception as e:
            if attempt < 2 and ("503" in str(e) or "UNAVAILABLE" in str(e)):
                time.sleep(3 * (attempt + 1))
                continue
            return {"status": "engine_error", "message": str(e)}
