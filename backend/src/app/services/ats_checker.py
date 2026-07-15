import json
import logging
import httpx
from src.app.config import settings

logger = logging.getLogger(__name__)

def evaluate_resume_ats(profile_data: dict, target_role: str = None) -> dict:
    """
    Evaluates the parsed resume details against standard ATS parameters or a target role.
    If OPENAI_API_KEY is present, uses OpenAI API to evaluate.
    Otherwise, uses rule-based heuristic check.
    """
    if settings.OPENAI_API_KEY:
        try:
            feedback = evaluate_with_openai(profile_data, target_role)
            if feedback:
                return feedback
        except Exception as e:
            logger.error(f"Failed to check ATS with OpenAI: {e}. Falling back to rule-based ATS.")

    return rule_based_ats(profile_data, target_role)

def evaluate_with_openai(profile_data: dict, target_role: str = None) -> dict:
    """
    Sends structured profile to OpenAI to obtain ATS score and lists of suggestions.
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    role_info = f"target role: '{target_role}'" if target_role else "general industry standards"
    
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an experienced recruiter and ATS audit system. Evaluate the candidate profile and output an ATS score and improvement recommendations conforming exactly to the JSON schema."
            },
            {
                "role": "user",
                "content": f"Please evaluate this candidate profile against {role_info}:\n{json.dumps(profile_data, indent=2)}"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "ats_eval_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "ats_score": {
                            "type": "integer",
                            "description": "ATS score from 0 to 100"
                        },
                        "ats_suggestions": {
                            "type": "object",
                            "properties": {
                                "missing_skills": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Key skills or keywords missing from the profile for the target role"
                                },
                                "formatting_suggestions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Suggestions on resume formatting and presentation"
                                },
                                "experience_improvements": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Suggestions on improving descriptions of experience or projects"
                                }
                            },
                            "required": ["missing_skills", "formatting_suggestions", "experience_improvements"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["ats_score", "ats_suggestions"],
                    "additionalProperties": False
                }
            }
        }
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            logger.error(f"OpenAI ATS check failed with status code {response.status_code}: {response.text}")
            raise Exception("OpenAI API error")

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
