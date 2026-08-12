import logging
import httpx
from src.app.core.config import settings
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured

logger = logging.getLogger(__name__)

def classify_email(subject: str, body: str) -> str:
    """
    Classifies incoming job emails into categories:
    - Interview Invite
    - Rejection
    - Action Required
    - Status Update
    - Unrelated
    """
    subject_lower = subject.lower()
    body_lower = body.lower()
    combined = f"{subject_lower} {body_lower}"

    # Heuristic Keyword Check (high accuracy baseline)
    # 1. Rejection
    rejection_keywords = [
        "not moving forward", "unfortunately", "other candidates", "pursue other", 
        "thank you for your interest", "regret to inform", "filled the position",
        "decided to pass", "no longer under consideration"
    ]
    if any(k in combined for k in rejection_keywords):
        return "Rejection"

    # 2. Interview Invite
    invite_keywords = [
        "interview", "schedule a time", "calendar link", "speak with us", 
        "availabilities", "phone call", "availability to chat", "video call"
    ]
    if any(k in combined for k in invite_keywords):
        return "Interview Invite"

    # 3. Action Required
    action_keywords = [
        "assessment", "hackerank", "codility", "test", "submit transcript", 
        "provide references", "action required", "questionnaire"
    ]
    if any(k in combined for k in action_keywords):
        return "Action Required"

    # 4. Status Update / Confirmation
    confirmation_keywords = [
        "received your application", "thank you for applying", "under review", 
        "currently reviewing", "status of your application"
    ]
    if any(k in combined for k in confirmation_keywords):
        return "Status Update"

    # Fallback to LLM if configured for complex cases
    if is_llm_configured():
        try:
            return classify_with_openai(subject, body)
        except Exception as e:
            logger.error(f"Failed to classify email with LLM: {e}")

    return "Status Update"  # Default fallback classification

def classify_with_openai(subject: str, body: str) -> str:
    """
    Asks configured LLM to classify the email content.
    """
    headers, url, model = get_llm_headers_and_url()
    
    prompt = f"""
    Classify the following email from a company regarding a job application.
    Subject: {subject}
    Body:
    {body}
    
    Choose exactly one label from this list:
    - Interview Invite
    - Rejection
    - Action Required
    - Status Update
    - Unrelated
    
    Output ONLY the exact category name. Do not output any other characters.
    """
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an assistant that classifies recruitment emails."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            url,
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            classification = result["choices"][0]["message"]["content"].strip()
            # Clean punctuation if LLM outputs extra characters
            classification = classification.replace("-", "").strip()
            valid_categories = ["Interview Invite", "Rejection", "Action Required", "Status Update", "Unrelated"]
            for cat in valid_categories:
                if cat.lower() in classification.lower():
                    return cat
            return "Status Update"
        else:
            raise Exception("OpenAI API classification error")
