import logging
import random
import asyncio
from typing import List, Dict
from linkedin_api import Linkedin

from src.app.services.search.base import BaseSearchProvider
from src.app.core.security import decrypt_credential

logger = logging.getLogger(__name__)

class LinkedInScraperProvider(BaseSearchProvider):
    def __init__(self, email: str = None, encrypted_password: str = None):
        self.email = email
        self.encrypted_password = encrypted_password
        self.client = None

    def authenticate(self):
        """Authenticates with LinkedIn using the provided credentials."""
        if not self.email or not self.encrypted_password:
            logger.error("LinkedIn credentials not provided.")
            return False
        
        try:
            password = decrypt_credential(self.encrypted_password)
            if not password:
                logger.error("Failed to decrypt LinkedIn password.")
                return False
            
            # Note: Using Linkedin API. This handles login and session cookies.
            self.client = Linkedin(self.email, password)
            logger.info("Successfully authenticated with LinkedIn API.")
            return True
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False

    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Search for jobs on LinkedIn using the unofficial API.
        Extracts company info, job link, and description.
        """
        if not self.client:
            if not self.authenticate():
                return []

        logger.info(f"Searching LinkedIn for '{query}' in '{country}'...")
        all_jobs = []
        
        try:
            # Map common country codes to full names or LinkedIn regions
            location = country
            if country.lower() == "us":
                location = "United States"
            elif country.lower() == "uk" or country.lower() == "gb":
                location = "United Kingdom"
            
            # The `linkedin_api` has `search_jobs`, but its parameters can change. 
            # We'll use it in a thread/async wrapper because it's blocking.
            def fetch_jobs():
                # search_jobs signature: keywords, location_name, limit, etc.
                return self.client.search_jobs(keywords=query, location_name=location, limit=10)
            
            # Run the blocking network call in a separate thread
            raw_jobs = await asyncio.to_thread(fetch_jobs)
            
            if not raw_jobs:
                logger.info("No jobs found on LinkedIn for this query.")
                return []

            for job in raw_jobs:
                # Fetch detailed job info to get description (which might contain the email)
                job_id = job.get('dashEntityUrn', '').split(':')[-1]
                if not job_id:
                    continue
                
                # Fetching details for each job can be slow, but user asked for deep extraction.
                def fetch_job_detail():
                    try:
                        return self.client.get_job(job_id)
                    except Exception:
                        return None
                
                job_detail = await asyncio.to_thread(fetch_job_detail)
                
                title = job.get('title', 'Unknown Title')
                company_details = job.get('companyDetails', {})
                company_name = "Unknown Company"
                
                # Extract company name safely
                if 'company' in company_details:
                    # Sometimes it's a dict, sometimes a list
                    if isinstance(company_details['company'], list) and len(company_details['company']) > 0:
                        company_name = company_details['company'][0].get('name', 'Unknown Company')
                    elif isinstance(company_details['company'], dict):
                        company_name = company_details['company'].get('name', 'Unknown Company')
                elif 'companyName' in job:
                    company_name = job.get('companyName')
                
                job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                location_name = job.get('formattedLocation', location)
                
                description = "No description available"
                if job_detail:
                    description = job_detail.get('description', {}).get('text', description)
                
                # We do not extract email here as SearchAggregator already has `extract_emails_from_text` 
                # which processes the description! We just pass the description back.
                
                all_jobs.append({
                    "title": title,
                    "company": company_name,
                    "location": location_name,
                    "description": description,
                    "url": job_url,
                    "opportunity_type": "job",
                    "source": "LinkedIn Plugin",
                    "raw_data": job
                })
                
                # Small delay to simulate human reading / avoid rate limits on detailed fetches
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            logger.error(f"Error during LinkedIn job search: {e}", exc_info=True)
            
        logger.info(f"LinkedIn Scraper finished. Found {len(all_jobs)} jobs.")
        return all_jobs
