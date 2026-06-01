import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Using key: {api_key[:8]}..." if api_key else "ERROR: No API key found in .env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(model="gemini-2.5-flash", contents="Say hello.")
print(response.text)