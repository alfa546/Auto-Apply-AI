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

    async def run_rag_guided_search(self, db: Session, user_id: str):
        """
        Smooth RAG & Preferences Guided Job Search Agent:
        1. Reads user preferences (target countries, target roles, employment types).
        2. Reads candidate RAG resume profile skills & keywords from vector DB / Profile model.
        3. Formulates optimized search queries blending RAG skills + user target preferences.
        4. Runs search aggregator across preferred countries and evaluates RAG match scores.
        """
        from src.app.models import Profile, UserSettings
        from src.app.services.matching.matcher import MatchingEngine
        
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

        # Extract target countries or default to US/GB/DE/CA/AE
        target_countries = ["us", "ca", "gb", "de", "ae"]
        if user_settings and user_settings.preferred_countries:
            country_map = {
                "united states": "us", "canada": "ca", "united kingdom": "gb", 
                "germany": "de", "netherlands": "nl", "switzerland": "ch", 
                "sweden": "se", "australia": "au", "singapore": "sg", 
                "united arab emirates": "ae", "saudi arabia": "sa", "japan": "jp"
            }
            extracted_codes = []
            for country_str in user_settings.preferred_countries:
                c_clean = country_str.lower()
                for name_key, code in country_map.items():
                    if name_key in c_clean or code in c_clean:
                        extracted_codes.append(code)
                        break
            if extracted_codes:
                target_countries = list(set(extracted_codes))

        # Extract RAG resume skills & target roles
        rag_skills = (profile.skills if profile and profile.skills else ["Python", "FastAPI", "React", "Next.js"])
        target_roles = (user_settings.target_roles if user_settings and user_settings.target_roles else ["Full Stack Developer", "AI Engineer"])

        # Formulate RAG search queries
        search_queries = []
        for role in target_roles[:2]:
            top_skills = " ".join(rag_skills[:2]) if rag_skills else ""
            search_queries.append(f"{role} {top_skills}".strip())

        if profile and profile.employment_types and any("internship" in et.lower() for et in profile.employment_types):
            search_queries.append(f"{target_roles[0] if target_roles else 'Developer'} Internship")

        total_new_opportunities = 0
        for country in target_countries[:3]:
            for query in search_queries:
                count = await self.run_aggregation(db=db, query=query, country=country)
                total_new_opportunities += count

        # Run RAG Matcher evaluation for unrated jobs
        matcher = MatchingEngine()
        unrated_jobs = db.query(JobFound).all()
        for job in unrated_jobs:
            eval_res = await matcher.evaluate_job_match(db=db, user_id=user_id, job_id=job.id)
            logger.info(f"RAG Evaluated Job {job.id} ({job.title}): Score={eval_res.get('score')} Match={eval_res.get('is_match')}")

        return total_new_opportunities
