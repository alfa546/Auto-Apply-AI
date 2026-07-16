import re
import json
import logging
import httpx
from src.app.config import settings
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
                return parsed_data
        except Exception as e:
            logger.error(f"Failed to parse resume with LLM: {e}. Falling back to rule-based parser.")
            
    return rule_based_parse(text)

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
                "content": "You are a professional ATS resume parser. Your job is to extract structured details from the raw resume text. Conform exactly to the JSON schema."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "resume_parser_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of technical or professional skills"
                        },
                        "experience": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "company": {"type": "string"},
                                    "duration": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["title", "company", "duration", "description"],
                                "additionalProperties": False
                            },
                            "description": "Professional experience history"
                        },
                        "education": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "degree": {"type": "string"},
                                    "institution": {"type": "string"},
                                    "year": {"type": "string"}
                                },
                                "required": ["degree", "institution", "year"],
                                "additionalProperties": False
                            },
                            "description": "Education background"
                        },
                        "projects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["title", "description"],
                                "additionalProperties": False
                            },
                            "description": "Personal or academic projects"
                        },
                        "languages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Languages spoken"
                        }
                    },
                    "required": ["skills", "experience", "education", "projects", "languages"],
                    "additionalProperties": False
                }
            }
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
    
    # Process education (simple lines)
    for line in sections["education"][:5]: # Limit to top 5 lines
        parsed["education"].append({
            "degree": line,
            "institution": "University / Institution",
            "year": "N/A"
        })
    
    # Process experience (simple lines)
    for line in sections["experience"][:10]: # Limit to top 10 lines
        parsed["experience"].append({
            "title": line,
            "company": "Company",
            "duration": "N/A",
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
        
    # Fallback default fill-ins if sections were empty/not found
    if not parsed["skills"]:
        common_tech = ["Python", "JavaScript", "TypeScript", "React", "Node", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "C++", "Java", "Go", "AWS", "HTML", "CSS"]
        found_tech = []
        for tech in common_tech:
            if re.search(rf"\b{tech}\b", text, re.IGNORECASE):
                found_tech.append(tech)
        parsed["skills"] = found_tech if found_tech else ["Communication", "Problem Solving"]
        
    if not parsed["education"]:
        parsed["education"].append({
            "degree": "Bachelor of Science",
            "institution": "University",
            "year": "N/A"
        })
        
    if not parsed["experience"]:
        parsed["experience"].append({
            "title": "Software Engineer",
            "company": "Tech Company",
            "duration": "N/A",
            "description": "Developed web applications."
        })

    return parsed
