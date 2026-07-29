import re
import asyncio
import logging
from sqlalchemy.orm import Session
from src.app.models import JobFound
from src.app.services.search.adzuna import AdzunaProvider
from src.app.services.search.jooble import JoobleProvider
from src.app.services.search.boards import GreenhouseProvider, LeverProvider
from src.app.services.search.rss import RSSProvider

logger = logging.getLogger(__name__)

class SearchAggregator:
    def __init__(self):
        self.providers = [
            AdzunaProvider(),
            JoobleProvider(),
            GreenhouseProvider(),
            LeverProvider(),
            RSSProvider()
        ]

    async def run_aggregation(self, db: Session, query: str, country: str = "us"):
        """
        Runs all active search providers, aggregates findings, filters duplicates,
        and saves unique records into the database.
        """
        logger.info(f"Starting Search Aggregator pipeline for query: '{query}' in country: '{country}'")
        
        # Run all providers concurrently
        tasks = [provider.search(query, country) for provider in self.providers]
        gathered_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_opportunities = []
        for res in gathered_results:
            if isinstance(res, Exception):
                logger.error(f"Search provider raised an exception: {res}", exc_info=True)
            elif isinstance(res, list):
                all_opportunities.extend(res)

        logger.info(f"Aggregated {len(all_opportunities)} raw opportunities from all providers.")

        # Deduplicate and save to database
        new_records_count = 0
        seen_urls = set()

        for opp in all_opportunities:
            url = opp.get("url")
            if not url:
                continue
            
            # Skip duplicates within the current batch
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Check if opportunity already exists in database
            exists = db.query(JobFound).filter(JobFound.url == url).first()
            if not exists:
                description = opp.get("description", "")
                company = opp.get("company", "Company")
                
                # Extract hiring emails
                from src.app.services.email_extractor import extract_emails_from_text, select_best_hiring_email
                extracted_emails = extract_emails_from_text(description)
                company_email = select_best_hiring_email(extracted_emails, company)
                
                # Fallback email structure if no explicit email found in description
                if not company_email:
                    clean_comp = re.sub(r'[^a-zA-Z0-9]', '', company.lower())
                    company_email = f"careers@{clean_comp}.com"

                # Save new job found record
                job_record = JobFound(
                    title=opp.get("title"),
                    company=company,
                    company_email=company_email,
                    extracted_emails=extracted_emails,
                    location=opp.get("location"),
                    description=description,
                    url=url,
                    salary=opp.get("salary"),
                    opportunity_type=opp.get("opportunity_type", "job"),
                    raw_data=opp.get("raw_data", {})
                )
                db.add(job_record)
                new_records_count += 1

        if new_records_count > 0:
            db.commit()
            
        logger.info(f"Aggregator pipeline complete. Saved {new_records_count} new opportunities to the database.")
        return new_records_count
