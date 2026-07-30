import logging
import httpx
from typing import List, Dict
from src.app.config import settings
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

class JoobleProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Queries the Jooble API. If credentials are not set, returns fallback mock jobs.
        """
        api_key = settings.JOOBLE_API_KEY

        if not api_key or api_key == "mock":
            logger.info("Jooble API key not configured.")
            return []

        url = f"https://jooble.org/api/{api_key}"
        payload = {
            "keywords": query,
            "location": country
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    # Jooble returns list of jobs in 'jobs' key
                    for job in data.get("jobs", []):
                        results.append({
                            "title": job.get("title", "N/A"),
                            "company": job.get("company", "N/A"),
                            "location": job.get("location", "N/A"),
                            "description": job.get("snippet", ""),
                            "url": job.get("link", ""),
                            "salary": job.get("salary", "N/A"),
                            "opportunity_type": "job",
                            "raw_data": job
                        })
                    return results
                else:
                    logger.error(f"Jooble API returned error status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Jooble API request failed: {e}")

        return []

    def _get_mock_jobs(self, query: str, country: str) -> List[Dict]:
        """
        Generates realistic developer jobs for testing and demonstration.
        """
        normalized_query = query.lower()
        if "react" in normalized_query:
            role = "React Frontend Developer"
            skills = "React, Next.js, Redux, Tailwind"
        elif "python" in normalized_query or "fastapi" in normalized_query:
            role = "Python Backend Developer"
            skills = "Python, FastAPI, SQL, Git"
        else:
            role = f"Software Engineer ({query})"
            skills = f"{query}, Python/React"

        return [
            {
                "title": role,
                "company": "OpenAI",
                "location": f"Remote, {country.upper()}",
                "description": f"We are searching for a developer proficient in {skills} to help build next-generation AI interfaces and backends.",
                "url": f"https://openai.com/careers/mock-{normalized_query.replace(' ', '-')}-1",
                "salary": "$150,000 - $190,000",
                "opportunity_type": "job",
                "raw_data": {"source": "jooble_mock"}
            },
            {
                "title": f"Staff {role}",
                "company": "Cloudflare",
                "location": f"Austin, TX, {country.upper()}",
                "description": f"Lead engineering teams scaling security products. Proficiency in {skills} is highly desired.",
                "url": f"https://cloudflare.com/careers/mock-{normalized_query.replace(' ', '-')}-2",
                "salary": "$180,000 - $220,000",
                "opportunity_type": "job",
                "raw_data": {"source": "jooble_mock"}
            }
        ]
