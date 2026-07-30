import logging
import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict
from src.app.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)

class RSSProvider(BaseSearchProvider):
    def __init__(self):
        # We can seed some default RSS feed URLs for hackathons/scholarships
        self.feeds = [
            {
                "url": "https://devpost.com/feed",
                "opportunity_type": "hackathon",
                "source": "Devpost"
            }
        ]

    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Parses RSS feeds for hackathons or scholarships and filters by search query keywords.
        """
        results = []
        normalized_query = query.lower()

        async with httpx.AsyncClient(timeout=10.0) as client:
            for feed in self.feeds:
                try:
                    response = await client.get(feed["url"])
                    if response.status_code == 200:
                        results.extend(self._parse_rss_content(response.text, query, feed["opportunity_type"], feed["source"]))
                except Exception as e:
                    logger.warning(f"Failed to fetch RSS feed {feed['url']}: {e}.")

        return results

    def _parse_rss_content(self, xml_text: str, query: str, opportunity_type: str, source: str) -> List[Dict]:
        results = []
        normalized_query = query.lower()
        try:
            root = ET.fromstring(xml_text)
            channel = root.find("channel")
            if channel is None:
                return results

            for item in channel.findall("item"):
                title = item.find("title")
                title_text = title.text if title is not None else ""
                
                link = item.find("link")
                link_text = link.text if link is not None else ""

                desc = item.find("description")
                desc_text = desc.text if desc is not None else ""

                # Filter by keyword match
                if normalized_query in title_text.lower() or normalized_query in desc_text.lower():
                    results.append({
                        "title": title_text,
                        "company": source,
                        "location": "Online",
                        "description": desc_text[:300] + "..." if desc_text else "",
                        "url": link_text,
                        "salary": "N/A",
                        "opportunity_type": opportunity_type,
                        "raw_data": {"source": f"{source}_rss"}
                    })
        except Exception as e:
            logger.error(f"Error parsing RSS XML structure: {e}")
        return results

    def _get_mock_opportunities(self, query: str, opportunity_type: str, source: str) -> List[Dict]:
        normalized_query = query.lower()
        if opportunity_type == "hackathon":
            return [
                {
                    "title": f"Global {query.capitalize()} AI Hackathon 2026",
                    "company": source,
                    "location": "Online / Global",
                    "description": f"Compete with developers worldwide to build innovative solutions using {query}.",
                    "url": f"https://devpost.com/hackathons/mock-{normalized_query}-hackathon",
                    "salary": "Prizes: $15,000",
                    "opportunity_type": "hackathon",
                    "raw_data": {"source": f"{source}_mock"}
                }
            ]
        else:
            return [
                {
                    "title": f"{query.capitalize()} Excellence Scholarship",
                    "company": "EduFoundation",
                    "location": "United States",
                    "description": "Financial assistance program for outstanding students pursuing studies in computer science.",
                    "url": "https://example.org/scholarships/mock-cs-excellence",
                    "salary": "Grant: $10,000",
                    "opportunity_type": "scholarship",
                    "raw_data": {"source": "scholarship_mock"}
                }
            ]
