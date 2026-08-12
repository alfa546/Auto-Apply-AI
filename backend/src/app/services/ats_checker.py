import json
import logging
import httpx
from fastapi import HTTPException, status
from src.app.core.config import settings
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured, detect_llm_provider

logger = logging.getLogger(__name__)

def parse_llm_response(response: dict, provider: str) -> str:
    """
    Extracts the text content from LLM API responses across various providers.
    """
    try:
        if provider == "gemini" and "candidates" in response:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        elif provider == "anthropic" and "content" in response and isinstance(response["content"], list):
            return response["content"][0]["text"]
        
        # Default / OpenAI / Groq / DeepSeek format
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Failed to parse LLM response for provider {provider}: {e}")
        return ""

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
    key = settings.OPENAI_API_KEY or settings.GEMINI_API_KEY or "free-local"
    provider = detect_llm_provider(key)
    
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
            content = parse_llm_response(result, provider).strip()
            if not content:
                return None
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
    summary = " ".join(lines[:3]) if lines else ""

    if is_llm_configured():
        try:
            headers, url, model = get_llm_headers_and_url()
            key = settings.OPENAI_API_KEY or settings.GEMINI_API_KEY or "free-local"
            provider = detect_llm_provider(key)
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
                    result = res.json()
                    content = parse_llm_response(result, provider).strip()
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
        "skills": extracted_skills or [],
        "summary": summary,
        "experience": [],
        "education": [],
        "projects": []
    }

def rule_based_ats(profile_data: dict, target_role: str = None) -> dict:
    """
    Computes standard heuristic metrics to rate a profile and suggest updates.
    Returns detailed breakdown of 4 ATS categories.
    """
    skills = profile_data.get("skills", [])
    experience = profile_data.get("experience", [])
    education = profile_data.get("education", [])
    projects = profile_data.get("projects", [])
    
    missing_skills = []
    formatting_suggestions = []
    experience_improvements = []
    
    # 1. Formatting & Structure Score (0-100)
    formatting_score = 70
    if not education:
        formatting_score -= 15
        formatting_suggestions.append("Education section appears to be missing or could not be detected.")
    if not experience:
        formatting_score -= 20
        formatting_suggestions.append("Work experience section is missing. Add your professional history.")
    if not formatting_suggestions:
        formatting_suggestions.append("Ensure your contact details, including LinkedIn and GitHub, are prominent at the top.")
        formatting_suggestions.append("Use standard bullet points with action verbs (e.g., Developed, Orchestrated, Optimized) instead of paragraphs.")
    
    # 2. Technical Skill Density Score (0-100)
    keyword_density_score = 50
    if len(skills) < 5:
        keyword_density_score = 30
        missing_skills.append("Add more technical/industry skills (aim for at least 8-10 skills).")
    elif len(skills) < 8:
        keyword_density_score = 55
        missing_skills.append("Add a few more relevant technical skills to improve keyword density.")
    elif len(skills) <= 15:
        keyword_density_score = 85
    else:
        keyword_density_score = 95
    
    # Check target role skill match
    if target_role:
        target_role_lower = target_role.lower()
        keywords_matched = any(
            s.lower() in target_role_lower or any(word in s.lower() for word in target_role_lower.split())
            for s in skills
        )
        if not keywords_matched:
            keyword_density_score -= 15
            missing_skills.append(f"Add key skills matching the target role '{target_role}'.")
    
    # 3. Action Verbs & Impact Score (0-100)
    action_verbs_score = 60
    action_verbs = ['developed', 'engineered', 'architected', 'implemented', 'optimized', 'led', 'managed', 
                    'created', 'designed', 'built', 'improved', 'increased', 'reduced', 'launched', 'delivered']
    
    has_strong_verbs = False
    if experience:
        for exp in experience:
            desc = exp.get("description", "").lower()
            if any(verb in desc for verb in action_verbs):
                has_strong_verbs = True
                break
        if not has_strong_verbs:
            action_verbs_score = 40
            experience_improvements.append("Use stronger action verbs (e.g., 'Engineered', 'Optimized', 'Architected') to describe your achievements.")
    
    # Check experience description quality
    if experience:
        for exp in experience:
            desc = exp.get("description", "")
            if len(desc) < 30:
                action_verbs_score -= 10
                experience_improvements.append(f"Elaborate on your role as '{exp.get('title')}' at '{exp.get('company')}'. Describe achievements, metrics, and technologies used.")
                break
    
    # 4. Section Completeness Score (0-100)
    section_completeness_score = 60
    if education:
        section_completeness_score += 10
    if experience:
        section_completeness_score += 10
    if skills and len(skills) >= 5:
        section_completeness_score += 10
    if projects:
        section_completeness_score += 10
    
    # Calculate overall score (weighted average)
    overall_score = int((
        formatting_score * 0.25 +
        keyword_density_score * 0.25 +
        action_verbs_score * 0.25 +
        section_completeness_score * 0.25
    ))
    
    # Cap score boundaries
    overall_score = max(30, min(95, overall_score))
    
    # Additional improvements
    if not projects:
        experience_improvements.append("Consider adding personal or academic projects to show practical application of skills.")
    if not experience:
        experience_improvements.append("No professional work experience detected. Add internships, freelance, or contract roles to strengthen your profile.")

    return {
        "ats_score": overall_score,
        "formatting_score": min(100, formatting_score),
        "keyword_density_score": min(100, keyword_density_score),
        "action_verbs_score": min(100, action_verbs_score),
        "section_completeness_score": min(100, section_completeness_score),
        "ats_suggestions": {
            "missing_skills": missing_skills,
            "formatting_suggestions": formatting_suggestions,
            "experience_improvements": experience_improvements
        }
    }
