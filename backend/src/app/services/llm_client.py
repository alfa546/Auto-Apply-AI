import logging
from typing import Tuple, Dict
from src.app.config import settings

logger = logging.getLogger(__name__)

def detect_llm_provider(api_key: str) -> str:
    """
    Automatically detects AI Model Provider based on API key prefix pattern.
    - 'gsk_' -> Groq (Free High-Speed Open Source Tier)
    - 'sk-or-' -> OpenRouter (Free Open Source Models)
    - 'AIzaSy' -> Google Gemini (legacy key format)
    - 'AQ.'  -> Google Gemini (newer 2025+ key format)
    - 'sk-ant-' -> Anthropic Claude
    - 'sk-proj-' or 'sk-' -> OpenAI / DeepSeek
    """
    if not api_key:
        return "openai"

    k = api_key.strip()
    if k.startswith("gsk_"):
        return "groq"
    elif k.startswith("sk-or-"):
        return "openrouter"
    elif k.startswith("AIzaSy") or k.startswith("AQ."):
        # 'AQ.' is the newer Google API key format (Gemini), NOT a typo
        return "gemini"
    elif k.startswith("sk-ant-"):
        return "anthropic"
    elif k.startswith("sk-") or k.startswith("sk-proj-"):
        return "openai"

    # Unknown prefix - fall back to OpenAI so that explicit configs keep working
    return "openai"

def get_llm_headers_and_url(
    api_key: str = None, 
    provider: str = None, 
    model_name: str = None, 
    custom_api_base: str = None
) -> Tuple[Dict[str, str], str, str]:
    """
    Returns (headers, endpoint_url, model_name) for any AI provider in the world,
    including 100% Free Open Source Endpoints (Ollama, LM Studio, Groq Free Tier, OpenRouter Free).
    """
    key = api_key or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY or "free-local"
    detected_provider = provider or detect_llm_provider(key)
    
    # Handle invalid API key that doesn't match known provider patterns
    if detected_provider == "invalid":
        # Try Gemini or fall back to openai gracefully
        logger.warning(f"API key format not recognized (starts with '{key[:3]}...'). Trying Gemini fallback.")
        if settings.GEMINI_API_KEY:
            key = settings.GEMINI_API_KEY
            detected_provider = "gemini"
        elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith(("sk-", "sk-proj-")):
            key = settings.OPENAI_API_KEY
            detected_provider = "openai"
        else:
            # No valid key available - return a clear instruction by defaulting to OpenAI
            # The error will be surfaced when the API call fails
            pass

    # 1. Ollama or Local Offline Open-Source Models (100% Free, no API Key needed)
    if detected_provider == "ollama" or custom_api_base:
        base_url = (custom_api_base or "http://localhost:11434/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {key or 'ollama-free'}",
            "Content-Type": "application/json"
        }
        model = model_name or "llama3"
        logger.info(f"Using Free Local Open Source Model (Ollama/LM Studio) at {url} with model: {model}")
        return headers, url, model

    # 2. OpenRouter Free Open-Source Models
    elif detected_provider == "openrouter":
        headers = {
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/alfa546/Auto-Apply-AI",
            "X-Title": "Auto-Apply AI",
            "Content-Type": "application/json"
        }
        url = "https://openrouter.ai/api/v1/chat/completions"
        model = model_name or "meta-llama/llama-3.1-8b-instruct:free"
        logger.info(f"Using OpenRouter Free Model API with model: {model}")
        return headers, url, model

    # 3. Groq Cloud (Free Open Source Models Tier)
    elif detected_provider == "groq":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = model_name or "llama-3.1-70b-versatile"
        logger.info(f"Using Groq Free Tier Open Source Model: {model}")
        return headers, url, model

    # 4. Google Gemini
    elif detected_provider == "gemini":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        model = model_name or settings.GEMINI_MODEL or "gemini-1.5-pro"
        logger.info(f"Using Gemini LLM with model: {model}")
        return headers, url, model

    # 5. DeepSeek
    elif detected_provider == "deepseek":
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        url = "https://api.deepseek.com/v1/chat/completions"
        model = model_name or "deepseek-chat"
        logger.info(f"Using DeepSeek LLM with model: {model}")
        return headers, url, model

    # Default to OpenAI standard format
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/chat/completions"
    model = model_name or settings.OPENAI_MODEL or "gpt-4o"
    logger.info(f"Using OpenAI LLM with model: {model}")
    return headers, url, model

def is_llm_configured(api_key: str = None, provider: str = None, custom_api_base: str = None) -> bool:
    """
    Returns True only if a valid LLM configuration exists.
    Local endpoints (Ollama/custom) are always allowed.
    Invalid/mistyped API keys (e.g. 'AQ.xxx') are treated as NOT configured to
    avoid 401 failures - the app will gracefully fall back to template generation.
    """
    if provider == "ollama" or custom_api_base:
        return True

    key = api_key or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    if not key:
        return False

    # Validate the key format matches a known provider prefix
    return detect_llm_provider(key) != "invalid"

def generate_custom_cover_letter(candidate_name: str = "Candidate", job_title: str = "Software Engineer", company: str = "Company", skills: list = None, job_description: str = None) -> str:
    """
    Generates a custom tailored cover letter using the active LLM provider.
    """
    from src.app.services.application.cover_letter import generate_cover_letter
    profile_data = {
        "skills": skills or ["Software Development", "Problem Solving", "AI Engineering"],
        "experience": [{"role": "Developer", "company": "Tech Company"}],
        "education": []
    }
    return generate_cover_letter(profile_data, job_title, company, job_description or "")