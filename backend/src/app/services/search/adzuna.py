import logging
import httpx
from typing import List, Dict
from src.app.config import settings
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

class AdzunaProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Queries the Adzuna API. If credentials are not set, returns fallback mock jobs.
        """
        app_id = settings.ADZUNA_APP_ID
        app_key = settings.ADZUNA_APP_KEY

        if not app_id or not app_key or app_id == "mock" or app_key == "mock":
            logger.info("Adzuna API credentials not configured. Returning fallback mock jobs.")
            return self._get_mock_jobs(query, country)

        url = f"https://api.adzuna.com/v1/api/jobs/{country.lower()}/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 10,
            "what": query,
            "content-type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for job in data.get("results", []):
                        # Extract salary if available
                        salary_min = job.get("salary_min")
                        salary_max = job.get("salary_max")
                        salary_str = f"${salary_min} - ${salary_max}" if salary_min and salary_max else "N/A"
                        
                        results.append({
                            "title": job.get("title", "N/A"),
                            "company": job.get("company", {}).get("display_name", "N/A"),
                            "location": job.get("location", {}).get("display_name", "N/A"),
                            "description": job.get("description", ""),
                            "url": job.get("redirect_url", ""),
                            "salary": salary_str,
                            "opportunity_type": "job",
                            "raw_data": job
                        })
                    return results
                else:
                    logger.error(f"Adzuna API returned error status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Adzuna API request failed: {e}")

        # Fallback to mock on API error
        return self._get_mock_jobs(query, country)

    def _get_mock_jobs(self, query: str, country: str) -> List[Dict]:
        """
        Generates realistic developer jobs for testing and demonstration.
        """
        normalized_query = query.lower()
        if "react" in normalized_query:
            role = "Frontend React Developer"
            skills = "React, TypeScript, Next.js, CSS"
        elif "python" in normalized_query or "fastapi" in normalized_query:
            role = "Backend Python Engineer"
            skills = "Python, FastAPI, PostgreSQL, Docker"
        else:
            role = f"Software Engineer ({query})"
            skills = f"{query}, Git, SQL"

        return [
            {
                "title": role,
                "company": "Stripe",
                "location": f"Remote, {country.upper()}",
                "description": f"We are looking for a skilled professional with expertise in {skills} to join our engineering team.",
                "url": f"https://stripe.com/careers/mock-{normalized_query.replace(' ', '-')}-1",
                "salary": "$120,000 - $150,000",
                "opportunity_type": "job",
                "raw_data": {"source": "adzuna_mock"}
            },
            {
                "title": f"Senior {role}",
                "company": "Vercel",
                "location": f"San Francisco, {country.upper()}",
                "description": f"Join our core frameworks team focusing on cutting-edge features. Experience with {skills} required.",
                "url": f"https://vercel.com/careers/mock-{normalized_query.replace(' ', '-')}-2",
                "salary": "$160,000 - $200,000",
                "opportunity_type": "job",
                "raw_data": {"source": "adzuna_mock"}
            }
        ]
