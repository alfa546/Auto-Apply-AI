import logging
import httpx
import re
import html
from typing import List, Dict
from src.app.core.config import settings
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return " ".join(text.split())

class GreenhouseProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Crawls public Greenhouse boards for configured companies and filters by query keywords.
        """
        companies = settings.TRACKED_COMPANIES_GREENHOUSE
        results = []
        normalized_query = query.lower()

        async with httpx.AsyncClient(timeout=10.0) as client:
            for company in companies:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get("jobs", []):
                            title = job.get("title", "")
                            content_html = job.get("content", "")
                            # Case-insensitive keyword filter
                            if normalized_query in title.lower() or normalized_query in content_html.lower():
                                desc = clean_html(content_html)
                                if not desc:
                                    desc = f"Job vacancy for {title} at {company.capitalize()}."
                                results.append({
                                    "title": title,
                                    "company": company.capitalize(),
                                    "location": job.get("location", {}).get("name", "N/A"),
                                    "description": desc,
                                    "url": job.get("absolute_url", ""),
                                    "salary": "N/A",
                                    "opportunity_type": "job",
                                    "raw_data": job
                                })
                except Exception as e:
                    logger.warning(f"Failed to fetch Greenhouse board for {company}: {e}")

        # Fallback to empty list rather than mock, as it's secondary board crawling
        return results


class LeverProvider(BaseSearchProvider):
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Crawls public Lever boards for configured companies and filters by query keywords.
        """
        companies = settings.TRACKED_COMPANIES_LEVER
        results = []
        normalized_query = query.lower()

        async with httpx.AsyncClient(timeout=10.0) as client:
            for company in companies:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json() # Lever returns root list of postings
                        for posting in data:
                            title = posting.get("text", "")
                            desc_parts = []
                            main_desc = clean_html(posting.get("description", ""))
                            if main_desc:
                                desc_parts.append(main_desc)
                            
                            # Extract original requirement and responsibility lists from Lever API
                            for lst in posting.get("lists", []):
                                list_title = lst.get("text", "")
                                list_content = clean_html(lst.get("content", ""))
                                if list_title or list_content:
                                    desc_parts.append(f"### {list_title}\n{list_content}")

                            full_desc = "\n\n".join(desc_parts).strip()
                            if not full_desc:
                                full_desc = f"Job posting for {title} at {company.capitalize()}."

                            if normalized_query in title.lower() or normalized_query in full_desc.lower():
                                results.append({
                                    "title": title,
                                    "company": company.capitalize(),
                                    "location": posting.get("categories", {}).get("location", "N/A"),
                                    "description": full_desc,
                                    "url": posting.get("hostedUrl", ""),
                                    "salary": "N/A",
                                    "opportunity_type": "job",
                                    "raw_data": posting
                                })
                except Exception as e:
                    logger.info(f"Failed to fetch Lever board for {company} (might not exist or API error).")

        return results
