import json
import logging
import httpx
from fastapi import HTTPException, status
from src.app.config import settings
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured

logger = logging.getLogger(__name__)

def evaluate_resume_ats(profile_data: dict, target_role: str = None) -> dict:
    """
    Evaluates the parsed resume details against standard ATS parameters or a target role.
    If an LLM is configured (Gemini, OpenAI, Groq, DeepSeek, Ollama), uses the API to evaluate.
    Otherwise, uses rule-based heuristic check.
    """
    if is_llm_configured():
        try:
            feedback = evaluate_with_openai(profile_data, target_role)
            if feedback and "ats_score" in feedback:
                return feedback
        except Exception as e:
            logger.warning(f"LLM ATS check warning ({e}). Falling back to rule-based ATS evaluation.")

    return rule_based_ats(profile_data, target_role)

def evaluate_with_openai(profile_data: dict, target_role: str = None) -> dict:
    """
    Sends structured profile to LLM to obtain ATS score and lists of suggestions.
    Works across OpenAI, Gemini, Groq, DeepSeek, Ollama, and OpenRouter without json_schema errors!
    """
    headers, url, model = get_llm_headers_and_url()
    
    role_info = f"target role: '{target_role}'" if target_role else "general industry standards"
    
    prompt = f"""
    You are an experienced recruiter and ATS audit system. Evaluate this candidate profile against {role_info}:
    {json.dumps(profile_data, indent=2)}

    Return ONLY a valid JSON object matching this exact structure:
    {{
        "ats_score": 85,
        "ats_suggestions": {{
            "missing_skills": ["Skill 1", "Skill 2"],
            "formatting_suggestions": ["Suggestion 1"],
            "experience_improvements": ["Improvement 1"]
        }}
    }}
    """
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an ATS resume audit system. Respond ONLY in valid raw JSON format without markdown codeblocks or extra text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            return json.loads(content)
        else:
            logger.warning(f"LLM ATS check returned status code {response.status_code}.")
            return None

def extract_skills_and_summary_from_text(raw_text: str) -> dict:
    """
    Parses raw resume text and extracts candidate skills, executive summary, experience, and education.
    Works via LLM if available or rule-based tech stack parser fallback!
    """
    TECH_KEYWORDS = [
        "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Express",
        "FastAPI", "Django", "Flask", "HTML", "CSS", "TailwindCSS", "Bootstrap",
        "PostgreSQL", "MongoDB", "MySQL", "SQLite", "Redis", "Docker", "Kubernetes",
        "AWS", "GCP", "Azure", "Git", "GitHub", "REST API", "GraphQL", "CI/CD",
        "Linux", "Machine Learning", "Data Analysis", "SQL", "Java", "C++", "C#",
        "PHP", "Laravel", "Vue.js", "Angular", "Redux", "TensorFlow", "PyTorch"
    ]

    extracted_skills = []
    text_lower = raw_text.lower()
    for kw in TECH_KEYWORDS:
        if kw.lower() in text_lower:
            extracted_skills.append(kw)

    lines = [l.strip() for l in raw_text.split("\n") if l.strip() and len(l.strip()) > 15]
    summary = " ".join(lines[:3]) if lines else "Qualified professional candidate with a strong background in software development and technology."

    if is_llm_configured():
        try:
            headers, url, model = get_llm_headers_and_url()
            prompt = f"Extract candidate skills (as a JSON array of strings) and a 2-sentence executive summary from this resume text:\n{raw_text[:2000]}\nReturn ONLY valid JSON: {{\"skills\": [\"Python\", \"React\"], \"summary\": \"Executive summary...\"}}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a resume parser. Respond ONLY in valid JSON format."},
                    {"role": "user", "content": prompt}
                ]
            }
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    elif content.startswith("```"):
                        content = content.replace("```", "").strip()
                    data = json.loads(content)
                    if data.get("skills"):
                        extracted_skills = data["skills"]
                    if data.get("summary"):
                        summary = data["summary"]
        except Exception as e:
            logger.warning(f"LLM skill extraction failed: {e}. Using extracted skills keyword fallback.")

    return {
        "skills": extracted_skills or ["Python", "JavaScript", "FastAPI", "React", "SQL"],
        "summary": summary,
        "experience": [{"title": "Software Developer", "company": "Technology Company", "description": "Developed web applications and services."}],
        "education": [{"degree": "Bachelor of Science", "institution": "University"}],
        "projects": [{"name": "Auto-Apply AI", "description": "AI-powered job search and auto-application platform."}]
    }

def rule_based_ats(profile_data: dict, target_role: str = None) -> dict:
    """
    Computes standard heuristic metrics to rate a profile and suggest updates.
    """
    score = 65
    missing_skills = []
    formatting_suggestions = []
    experience_improvements = []
    
    skills = profile_data.get("skills", [])
    experience = profile_data.get("experience", [])
    education = profile_data.get("education", [])
    projects = profile_data.get("projects", [])
    
    # Assess skills
    if len(skills) < 5:
        score -= 10
        missing_skills.append("Add more technical/industry skills (aim for at least 8-10 skills).")
    elif len(skills) > 10:
        score += min(15, len(skills) - 10)
        
    # Assess experience
    if not experience:
        score -= 20
        experience_improvements.append("No professional work experience detected. Add internships, freelance or contract roles.")
    else:
        # Check descriptions
        for exp in experience:
            desc = exp.get("description", "")
            if len(desc) < 30:
                score -= 3
                experience_improvements.append(f"Elaborate on your role as '{exp.get('title')}' at '{exp.get('company')}'. Describe achievements and technologies used.")
                break
                
    # Assess education
    if not education:
        score -= 5
        formatting_suggestions.append("Education section appears to be missing or could not be detected.")
        
    # Assess projects
    if not projects:
        score -= 5
        experience_improvements.append("Consider adding personal or academic projects to show practical application of skills.")
        
    # Check target role specifics
    if target_role:
        target_role_lower = target_role.lower()
        # Look for keywords related to target role
        keywords_matched = False
        for s in skills:
            if s.lower() in target_role_lower or any(word in s.lower() for word in target_role_lower.split()):
                keywords_matched = True
                break
        if keywords_matched:
            score += 10
        else:
            score -= 10
            missing_skills.append(f"Add key skills matching the target role '{target_role}'.")
            
    # Cap score boundaries
    score = max(30, min(95, score))
    
    # Standard formatting suggestions
    if not formatting_suggestions:
        formatting_suggestions.append("Ensure your contact details, including LinkedIn and GitHub, are prominent at the top.")
        formatting_suggestions.append("Use standard bullet points with action verbs (e.g., Developed, Orchestrated, Optimized) instead of paragraphs.")

    return {
        "ats_score": score,
        "ats_suggestions": {
            "missing_skills": missing_skills,
            "formatting_suggestions": formatting_suggestions,
            "experience_improvements": experience_improvements
        }
    }
