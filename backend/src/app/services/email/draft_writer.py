import logging
import httpx
from src.app.config import settings

logger = logging.getLogger(__name__)

def generate_draft_reply(
    classification: str,
    sender: str,
    subject: str,
    body: str,
    candidate_profile: dict
) -> str:
    """
    Generates a professional email response draft based on classification.
    Uses OpenAI GPT if available, otherwise compiles from robust templates.
    """
    if settings.OPENAI_API_KEY:
        try:
            return generate_with_openai(classification, sender, subject, body, candidate_profile)
        except Exception as e:
            logger.error(f"Failed to generate draft reply with OpenAI: {e}. Falling back to templates.")
            
    return generate_from_template(classification, sender, candidate_profile)

def generate_with_openai(
    classification: str,
    sender: str,
    subject: str,
    body: str,
    candidate_profile: dict
) -> str:
    """
    Calls OpenAI Chat Completions to generate a professional email response draft.
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a professional email assistant. Write a professional reply to an email received from a recruiter.
    
    Received email details:
    - Sender: {sender}
    - Subject: {subject}
    - Body:
    {body}
    
    Classification of this email: {classification}
    
    Candidate details:
    - Name: {candidate_profile.get('name', 'Candidate')}
    - Skills: {', '.join(candidate_profile.get('skills', []))}
    
    Guidelines:
    - If 'Interview Invite': Express appreciation, confirm interest, and suggest 3 open morning/afternoon time slots for next week.
    - If 'Action Required': Acknowledge and state you are preparing the required documents/information and will share shortly.
    - If 'Rejection': Write a brief, courteous thank-you response requesting to stay connected for future opportunities.
    - Keep it short, professional, and clear. Do NOT add placeholder dates/times in brackets; write natural suggestions.
    - Output ONLY the body of the response email.
    """
    
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional email drafting assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    with httpx.Client(timeout=15.0) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise Exception("OpenAI API email drafting error")

def generate_from_template(classification: str, sender: str, candidate_profile: dict) -> str:
    """
    Compiles a template-based professional response.
    """
    name = candidate_profile.get("name", "Candidate")
    
    if classification == "Interview Invite":
        return f"""Thank you for reaching out! I am very excited about the opportunity to discuss the role further.

I would be glad to schedule a call. I am generally available next week on Monday and Wednesday mornings (between 9:00 AM and 11:30 AM EST), or Tuesday afternoons (between 1:00 PM and 4:00 PM EST). Please let me know if any of these slots work for you, or feel free to share your scheduling link.

Best regards,
{name}"""

    elif classification == "Action Required":
        return f"""Thank you for the update. 

I am currently compiling the requested information and will follow up shortly to provide the required documents. Please let me know if there is anything else you need in the meantime.

Best regards,
{name}"""

    elif classification == "Rejection":
        return f"""Thank you for letting me know about your decision. While I am disappointed, I sincerely appreciate the time you took to review my application.

I would love to stay in touch for any future opportunities that align with my background. I wish you and the team the best of luck in finding the right candidate.

Sincerely,
{name}"""

    else:
        # Default follow up thank you
        return f"""Thank you for the update. I appreciate you keeping me informed about the status of my application.

I look forward to hearing about the next steps.

Best regards,
{name}"""
