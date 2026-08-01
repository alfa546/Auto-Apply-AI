import logging
import httpx
from typing import List, Dict
from src.app.config import settings
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

class AdzunaProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Queries the Adzuna API. Returns empty list if credentials are not configured.
        """
        app_id = settings.ADZUNA_APP_ID
        app_key = settings.ADZUNA_APP_KEY

        if not app_id or not app_key:
            logger.info("Adzuna API credentials not configured.")
            return []

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

        return []
