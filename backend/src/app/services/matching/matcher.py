import re
import logging
from sqlalchemy.orm import Session
from src.app.models import User, Profile, UserSettings, JobFound
from src.app.config import settings
import httpx
import json
from src.app.services.llm_client import get_llm_headers_and_url, is_llm_configured

logger = logging.getLogger(__name__)

class MatchingEngine:
    async def evaluate_job_match(self, db: Session, user_id: str, job_id: int) -> dict:
        """
        Evaluates an opportunity against user settings (hard constraints) and profile (semantic search).
        Returns a dictionary with match result details:
            is_match: bool
            score: float (0.0 to 1.0)
            reasons: list of strings
        """
        reasons = []

        # 1. Fetch user data
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        job = db.query(JobFound).filter(JobFound.id == job_id).first()

        if not profile:
            return {"is_match": False, "score": 0.0, "reasons": ["Resume profile not uploaded/parsed."]}
        if not job:
            return {"is_match": False, "score": 0.0, "reasons": ["Job opportunity not found."]}

        # If user settings do not exist, create a default one
        if not user_settings:
            user_settings = UserSettings(user_id=user_id)
            db.add(user_settings)
            db.commit()
            db.refresh(user_settings)

        # 2. Run Hard Constraints Checks
        
        # A. Location & Preferred Countries Constraint
        if user_settings.preferred_countries:
            job_location = (job.location or "").lower()
            country_matched = False
            for country in user_settings.preferred_countries:
                if country.lower() in job_location:
                    country_matched = True
                    break
            if not country_matched:
                logger.info(f"Job {job_id} filtered out due to location constraint: {job.location}")
                return {
                    "is_match": False,
                    "score": 0.0,
                    "reasons": [f"Location '{job.location}' does not match preferred countries: {user_settings.preferred_countries}."]
                }

        # B. Remote Preference Constraint
        job_text = f"{job.title} {job.location} {job.description}".lower()
        is_remote_job = any(w in job_text for w in ["remote", "work from home", "wfh", "telecommute"])
        
        if user_settings.remote_preference == "remote" and not is_remote_job:
            # Reject if job is strictly onsite
            if "onsite" in job_text or "in-office" in job_text or "in person" in job_text:
                return {
                    "is_match": False,
                    "score": 0.0,
                    "reasons": ["User prefers remote roles, but this opportunity requires onsite work."]
                }
        elif user_settings.remote_preference == "onsite" and is_remote_job:
            # Check if strictly remote (no hybrid or onsite option mentioned)
            if "100% remote" in job_text or "fully remote" in job_text:
                return {
                    "is_match": False,
                    "score": 0.0,
                    "reasons": ["User prefers onsite roles, but this opportunity is fully remote."]
                }

        # C. Visa Sponsorship Constraint
        if user_settings.visa_sponsorship_required:
            # Look for negative sponsorship keywords in job description
            negative_sponsorship_phrases = [
                "no sponsorship",
                "does not offer sponsorship",
                "unable to sponsor",
                "cannot sponsor",
                "us citizen or green card only",
                "visa sponsorship is not available",
                "sponsor visa: no"
            ]
            if any(phrase in job_text for phrase in negative_sponsorship_phrases):
                return {
                    "is_match": False,
                    "score": 0.0,
                    "reasons": ["Visa sponsorship required, but the job description explicitly rules it out."]
                }

        # D. Salary Constraint
        if user_settings.min_salary:
            min_sal = float(user_settings.min_salary)
            job_salary_text = (job.salary or "").lower()
            # Extract numbers from salary text
            salary_numbers = [float(s) for s in re.findall(r"\d+[\d,]*", job_salary_text.replace(",", ""))]
            if salary_numbers:
                max_job_salary = max(salary_numbers)
                # Handle cases where salary is in thousands (e.g. 120 instead of 120000)
                if max_job_salary < 1000 and min_sal >= 1000:
                    max_job_salary *= 1000
                if max_job_salary < min_sal:
                    return {
                        "is_match": False,
                        "score": 0.0,
                        "reasons": [f"Offered salary {job.salary} is below user's minimum of ${min_sal:,.2f}."]
                    }

        # 3. Calculate Semantic Match via LLM
        semantic_score = 0.5 # Default middle score if embedding fails
        try:
            if is_llm_configured():
                headers, url, model = get_llm_headers_and_url()
                
                profile_data = {
                    "skills": profile.skills,
                    "experience": profile.experience,
                    "education": profile.education,
                }
                
                prompt = f"""
                You are an expert technical recruiter. Evaluate the candidate's profile against this job description.
                Job Title: {job.title}
                Job Description: {job.description}
                
                Candidate Profile:
                {json.dumps(profile_data, indent=2)}
                
                Return a JSON object with:
                - score: float between 0.0 and 1.0 representing how well the candidate matches the job.
                - reason: a short string explaining the score.
                
                Return ONLY valid JSON.
                """
                
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a recruitment AI. Respond ONLY in valid raw JSON format without markdown codeblocks or extra text."
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
                        content = response.json()["choices"][0]["message"]["content"].strip()
                        if content.startswith("```json"):
                            content = content.replace("```json", "").replace("```", "").strip()
                        elif content.startswith("```"):
                            content = content.replace("```", "").strip()
                        
                        try:
                            result = json.loads(content)
                            semantic_score = float(result.get("score", 0.5))
                            llm_reason = result.get("reason", "No specific reason provided.")
                            reasons.append(f"LLM Match Score: {semantic_score:.1%} - {llm_reason}")
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse LLM response: {content}")
                            reasons.append("LLM matching service returned invalid response, utilizing keyword fallback.")
                    else:
                        logger.warning(f"LLM matching service returned status {response.status_code}.")
                        reasons.append("LLM matching service returned an error, utilizing keyword fallback.")
            else:
                reasons.append("LLM matching service not configured, utilizing keyword fallback.")
        except Exception as ve:
            logger.error(f"Semantic evaluation failed: {ve}")
            reasons.append("LLM evaluation unavailable, utilizing keyword fallback.")

        # 4. Heuristic Keyword Matching
        keyword_score = 0.0
        matched_skills = []
        user_skills = profile.skills or []
        
        if user_skills:
            for skill in user_skills:
                # Use word-boundary regex to prevent partial match issues (e.g. 'Go' matching 'Google')
                pattern = rf"\b{re.escape(skill.lower())}\b"
                if re.search(pattern, job_text):
                    matched_skills.append(skill)
            
            keyword_score = len(matched_skills) / max(1, len(user_skills))
            # Normalize keyword score to a reasonable ceiling to prevent scaling issues
            keyword_score = min(1.0, keyword_score * 1.5)
            
            if matched_skills:
                reasons.append(f"Matched skills: {', '.join(matched_skills[:8])}.")
            else:
                reasons.append("No direct skill keywords found in the job description.")
        else:
            reasons.append("User profile does not contain any skills.")

        # 5. Composite Ranking Score
        composite_score = (0.6 * semantic_score) + (0.4 * keyword_score)
        
        is_above_threshold = composite_score >= settings.MATCHING_THRESHOLD
        if is_above_threshold:
            reasons.insert(0, f"Strong match score of {composite_score:.1%}.")
        else:
            reasons.insert(0, f"Match score of {composite_score:.1%} is below threshold of {settings.MATCHING_THRESHOLD:.1%}.")

        return {
            "is_match": is_above_threshold,
            "score": round(composite_score, 3),
            "reasons": reasons
        }
