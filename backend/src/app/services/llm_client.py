import logging
from src.app.config import settings

logger = logging.getLogger(__name__)

def get_llm_headers_and_url() -> tuple[dict, str, str]:
    """
    Returns headers, API URL, and model name depending on which API key is configured.
    Prioritizes Gemini if GEMINI_API_KEY is present, otherwise falls back to OpenAI.
    """
    if settings.GEMINI_API_KEY:
        headers = {
            "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        model = settings.GEMINI_MODEL
        logger.info(f"Using Gemini LLM with model: {model}")
        return headers, url, model
    elif settings.OPENAI_API_KEY:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://api.openai.com/v1/chat/completions"
        model = settings.OPENAI_MODEL
        logger.info(f"Using OpenAI LLM with model: {model}")
        return headers, url, model
    return {}, "", ""

def is_llm_configured() -> bool:
    return bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)
