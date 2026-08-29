import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def call_llm(prompt: str, fallback_snippet: str) -> str:
    """
    Call Gemini API if GEMINI_API_KEY is set.
    Otherwise, return the most relevant snippet with a fallback prefix.
    """
    api_key = settings.gemini_api_key
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"[fallback: LLM error] {fallback_snippet}"
    else:
        return f"[fallback: no LLM configured] {fallback_snippet}"
