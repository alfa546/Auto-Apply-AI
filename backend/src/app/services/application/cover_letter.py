import logging
import httpx
from src.app.core.config import settings
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured

logger = logging.getLogger(__name__)

def generate_cover_letter(profile_data: dict, job_title: str, company: str, job_description: str) -> str:
    """
    Generates a tailored cover letter for a candidate and target job opportunity.
    If an LLM is configured (Gemini or OpenAI), uses the API.
    Otherwise, falls back to a template-based generator.
    """
    if is_llm_configured():
        try:
            return generate_with_openai(profile_data, job_title, company, job_description)
        except Exception as e:
            logger.error(f"Failed to generate cover letter with LLM: {e}. Falling back to template-based generator.")
            
    return generate_from_template(profile_data, job_title, company)

def generate_with_openai(profile_data: dict, job_title: str, company: str, job_description: str) -> str:
    """
    Calls configured LLM Chat Completions to generate a professional cover letter.
    """
    headers, url, model = get_llm_headers_and_url()
    
    prompt = f"""
    You are a professional cover letter writer. Write a tailored, 3-paragraph cover letter for a candidate applying to the role of '{job_title}' at '{company}'.
    
    Candidate details:
    - Skills: {', '.join(profile_data.get('skills', []))}
    - Experience summary: {profile_data.get('experience', [])}
    - Education summary: {profile_data.get('education', [])}
    
    Job description:
    {job_description}
    
    Guidelines:
    - Make it professional, engaging, and concise (under 300 words).
    - Paragraph 1: State interest in the role of {job_title} at {company} and introduce the candidate's core background.
    - Paragraph 2: Align candidate skills ({', '.join(profile_data.get('skills', [])[:4])}) and experience with the job description.
    - Paragraph 3: State enthusiasm, mention resume attachment, and express interest in an interview.
    - Output ONLY the cover letter text, starting directly with the salutation and closing with a placeholder signature.
    """
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional cover letter writer. Output only the tailored cover letter text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
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
            return content.strip()
        else:
            logger.error(f"LLM cover letter call failed with status code {response.status_code}: {response.text}")
            raise Exception("LLM API error")

def generate_from_template(profile_data: dict, job_title: str, company: str) -> str:
    """
    Generates a professional cover letter using a local template.
    """
    skills = profile_data.get("skills", [])
    skills_str = ", ".join(skills[:5]) if skills else "software development, engineering best practices"
    
    latest_experience = "software developer"
    latest_company = "Tech Industry"
    experience = profile_data.get("experience", [])
    if experience:
        first_exp = experience[0]
        latest_experience = first_exp.get("title", latest_experience)
        latest_company = first_exp.get("company", latest_company)
        
    latest_education = "degree in Computer Science"
    education = profile_data.get("education", [])
    if education:
        first_edu = education[0]
        latest_education = first_edu.get("degree", latest_education)

    cover_letter = f"""Dear Hiring Team,

I am writing to express my strong interest in the {job_title} position at {company}. With a solid foundation in {skills_str}, combined with my academic and professional history, I am confident in my ability to deliver substantial value to your engineering team.

In my previous role as a {latest_experience} at {latest_company}, I gained hands-on experience designing, developing, and deploying robust applications while collaborating closely with cross-functional teams. Additionally, my {latest_education} has equipped me with strong theoretical foundations and problem-solving skills which I apply daily in my development work.

I am highly enthusiastic about the opportunity to contribute to the projects at {company} and would welcome the chance to discuss how my background aligns with your requirements in more detail. Thank you for your time and consideration.

Sincerely,
[Candidate Signature]"""

    return cover_letter
