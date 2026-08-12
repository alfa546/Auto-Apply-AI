import re
import json
import logging
import httpx
from fastapi import HTTPException, status
from src.app.core.config import settings
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured

logger = logging.getLogger(__name__)

def parse_resume_text(text: str) -> dict:
    """
    Parses raw resume text into structured sections.
    If an LLM is configured (Gemini or OpenAI), uses the API with structured JSON outputs.
    Otherwise, falls back to a rule-based parser.
    """
    if is_llm_configured():
        try:
            parsed_data = parse_resume_with_openai(text)
            if parsed_data:
                links_data = extract_contact_and_links(text)
                parsed_data.update(links_data)
                return parsed_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to parse resume with LLM: {e}. Falling back to rule-based parser.")
            
    parsed_data = rule_based_parse(text)
    links_data = extract_contact_and_links(text)
    parsed_data.update(links_data)
    return parsed_data

def extract_contact_and_links(text: str) -> dict:
    """
    Extract email, GitHub URL, portfolio URL, and LinkedIn URL using regular expressions.
    """
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    github_match = re.search(r'https?://(?:www\.)?github\.com/[\w-]+', text, re.IGNORECASE)
    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    portfolio_match = re.search(r'https?://(?!github|linkedin)[\w\.-]+\.[a-z]{2,}(?:/[\w\.-]*)*', text, re.IGNORECASE)
    
    return {
        "extracted_email": email_match.group(0) if email_match else None,
        "github_url": github_match.group(0) if github_match else None,
        "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
        "portfolio_url": portfolio_match.group(0) if portfolio_match else None
    }

def parse_resume_with_openai(text: str) -> dict:
    """
    Calls configured LLM API (Gemini or OpenAI) with a defined JSON Schema.
    """
    headers, url, model = get_llm_headers_and_url()
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional ATS resume parser. Your job is to extract structured details from the raw resume text.\n"
                    "Conform exactly to this JSON structure and return ONLY valid JSON:\n"
                    "{\n"
                    "  \"skills\": [\"List of technical or professional skills\"],\n"
                    "  \"experience\": [{\"title\": \"...\", \"company\": \"...\", \"duration\": \"...\", \"description\": \"...\"}],\n"
                    "  \"education\": [{\"degree\": \"...\", \"institution\": \"...\", \"year\": \"...\"}],\n"
                    "  \"projects\": [{\"title\": \"...\", \"description\": \"...\"}],\n"
                    "  \"languages\": [\"Languages spoken\"]\n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            url,
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            if response.status_code in [401, 429]:
                logger.error(f"LLM API quota reached or invalid (status {response.status_code})")
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="API Limit Reached")
            logger.error(f"LLM API call failed with status code {response.status_code}: {response.text}")
            raise Exception("LLM API error")

def rule_based_parse(text: str) -> dict:
    """
    Extracts structured fields from raw resume text using heuristics and keyword indexing.
    """
    headings = {
        "education": ["education", "academic history", "qualification", "academic background"],
        "skills": ["skills", "core competencies", "technical skills", "technologies", "expertise"],
        "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "languages": ["languages", "spoken languages", "language proficiency"]
    }
    
    lines = text.split("\n")
    sections = {k: [] for k in headings.keys()}
    current_section = None
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        
        # Check if line matches any section heading
        found_heading = False
        for sec, keywords in headings.items():
            for kw in keywords:
                if re.match(rf"^\s*(?:#+\s*)?{kw}\b", cleaned, re.IGNORECASE):
                    current_section = sec
                    found_heading = True
                    break
            if found_heading:
                break
        
        if found_heading:
            continue
            
        if current_section:
            sections[current_section].append(cleaned)
            
    parsed = {
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "languages": []
    }
    
    # Process skills (split by comma, bullet points)
    skills_text = " ".join(sections["skills"])
    if skills_text:
        skills = [s.strip() for s in re.split(r"[,•|;]|\band\b", skills_text) if s.strip()]
        # Remove empty or extremely long items
        parsed["skills"] = list(dict.fromkeys([s for s in skills if len(s) < 40]))[:30]
    
    # Process education (extract degree/institution/year patterns if possible)
    for line in sections["education"][:5]: # Limit to top 5 lines
        institution = "N/A"
        year = "N/A"
        # Try to extract institution (after comma, dash, or " at ")
        inst_match = re.search(r'(?:at|,|-)\s*([A-Za-z\s]+?)(?:,|\s+\d{4})?$', line, re.IGNORECASE)
        if inst_match and inst_match.group(1).strip() not in ("University", "College"):
            institution = inst_match.group(1).strip()
        # Try to extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', line)
        if year_match:
            year = year_match.group(0)
        parsed["education"].append({
            "degree": line,
            "institution": institution,
            "year": year
        })
    
    # Process experience (simple lines - only include real resume content, no placeholders)
    for line in sections["experience"][:10]: # Limit to top 10 lines
        parsed["experience"].append({
            "title": line,
            "company": "",
            "duration": "",
            "description": line
        })
        
    # Process projects
    for line in sections["projects"][:5]: # Limit to top 5 lines
        parsed["projects"].append({
            "title": line,
            "description": line
        })
        
    # Process languages
    lang_text = " ".join(sections["languages"])
    if lang_text:
        langs = [l.strip() for l in re.split(r"[,•|;]|\band\b", lang_text) if l.strip()]
        parsed["languages"] = list(dict.fromkeys(langs))
        
    # Fallback: extract real tech stack keywords from the resume text
    # Only include skills ACTUALLY found in the resume - never fabricate data
    if not parsed["skills"]:
        common_tech = ["Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Node", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", "MySQL", "Docker", "Kubernetes", "Git", "GitHub", "AWS", "GCP", "Azure", "HTML", "CSS", "TailwindCSS", "Redux", "GraphQL", "REST", "CI/CD", "Linux", "Machine Learning", "TensorFlow", "PyTorch", "Java", "C++", "C#", "Go", "PHP", "Laravel", "Vue.js", "Angular", "Bootstrap"]
        found_tech = []
        for tech in common_tech:
            if re.search(rf"\b{re.escape(tech)}\b", text, re.IGNORECASE):
                found_tech.append(tech)
        # Only set skills if something was actually found in the resume
        parsed["skills"] = found_tech

    # Note: No fabricated education/experience fallbacks.
    # Empty lists correctly signal that the resume parser could not extract those sections,
    # which is more honest than injecting fake "University" / "Tech Company" placeholder entries.

    return parsed
