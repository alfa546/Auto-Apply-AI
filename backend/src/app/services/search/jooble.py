import logging
import httpx
from typing import List, Dict
from src.app.config import settings
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

class JoobleProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us", api_key: str = None) -> List[Dict]:
        """
        Queries the Jooble API. Returns empty list if credentials are not configured.
        """
        key = api_key or settings.JOOBLE_API_KEY

        if not key:
            logger.info("Jooble API key not configured.")
            return []

        url = f"https://jooble.org/api/{key}"
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
                            "source": "Jooble",
                            "opportunity_type": "job",
                            "raw_data": job
                        })
                    return results
                else:
                    logger.error(f"Jooble API returned error status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Jooble API request failed: {e}")

        return []
