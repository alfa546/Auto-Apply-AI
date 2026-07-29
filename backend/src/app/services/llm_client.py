import logging
from typing import Tuple, Dict
from src.app.config import settings

logger = logging.getLogger(__name__)

def detect_llm_provider(api_key: str) -> str:
    """
    Automatically detects AI Model Provider based on API key prefix pattern.
    - 'sk-proj-' or 'sk-' -> OpenAI
    - 'AIzaSy' -> Google Gemini
    - 'gsk_' -> Groq
    - 'sk-ant-' -> Anthropic Claude
    """
    if not api_key:
        return "openai"
    
    k = api_key.strip()
    if k.startswith("gsk_"):
        return "groq"
    elif k.startswith("AIzaSy"):
        return "gemini"
    elif k.startswith("sk-ant-"):
        return "anthropic"
    elif k.startswith("sk-") or k.startswith("sk-proj-"):
        return "openai"
    
    return "openai"

def get_llm_headers_and_url(api_key: str = None, provider: str = None, model_name: str = None) -> Tuple[Dict[str, str], str, str]:
    """
    Returns (headers, endpoint_url, model_name) for any AI provider in the world.
    Supports OpenAI, Google Gemini, Groq, DeepSeek, Anthropic, and custom endpoints.
    """
    key = api_key or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    if not key:
        return {}, "", ""

    detected_provider = provider or detect_llm_provider(key)

    if detected_provider == "groq":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = model_name or "llama-3.1-70b-versatile"
        logger.info(f"Using Groq LLM with model: {model}")
        return headers, url, model

    elif detected_provider == "gemini":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        model = model_name or settings.GEMINI_MODEL or "gemini-1.5-pro"
        logger.info(f"Using Gemini LLM with model: {model}")
        return headers, url, model

    elif detected_provider == "deepseek":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://api.deepseek.com/v1/chat/completions"
        model = model_name or "deepseek-chat"
        logger.info(f"Using DeepSeek LLM with model: {model}")
        return headers, url, model

    # Default to OpenAI standard format (OpenAI, Anyscale, Together, Ollama)
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/chat/completions"
    model = model_name or settings.OPENAI_MODEL or "gpt-4o"
    logger.info(f"Using OpenAI LLM with model: {model}")
    return headers, url, model

def is_llm_configured(api_key: str = None) -> bool:
    return bool(api_key or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)
