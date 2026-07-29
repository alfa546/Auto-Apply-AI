import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Common regex pattern for email addresses
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Keywords indicating hiring / HR email
HIRING_KEYWORDS = ["hr", "careers", "jobs", "hiring", "talent", "recruiting", "apply", "contact", "info"]

def extract_emails_from_text(text: str) -> List[str]:
    """
    Finds all unique valid email addresses in a job description text.
    """
    if not text:
        return []
        
    matches = re.findall(EMAIL_REGEX, text)
    # Deduplicate while preserving order and lowercasing
    unique_emails = []
    for email in matches:
        clean_email = email.lower().strip('.')
        # Exclude dummy/generic example emails
        if clean_email not in unique_emails and not any(dummy in clean_email for dummy in ["example.com", "domain.com", "schema.org", "w3.org", "sentry.io"]):
            unique_emails.append(clean_email)
            
    return unique_emails

def select_best_hiring_email(emails: List[str], company_name: Optional[str] = None) -> Optional[str]:
    """
    Selects the most probable hiring/HR contact email from a list of extracted emails.
    """
    if not emails:
        return None
        
    # Prioritize emails containing hiring keywords
    for email in emails:
        for kw in HIRING_KEYWORDS:
            if kw in email.split('@')[0]:
                return email
                
    # If company_name provided, prioritize email domain matching company
    if company_name:
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        for email in emails:
            domain = email.split('@')[-1]
            if clean_company in domain:
                return email
                
    # Fallback to first found email
    return emails[0]
