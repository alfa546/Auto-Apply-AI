import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.main import app
from src.app.database import Base, get_db
from src.app.models import JobFound
from src.app.services.search.adzuna import AdzunaProvider
from src.app.services.search.jooble import JoobleProvider
from src.app.services.search.rss import RSSProvider
from src.app.services.search.boards import GreenhouseProvider, LeverProvider
from src.app.services.search.aggregator import SearchAggregator

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_search.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestSearchAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test_search.db"):
            try:
                os.remove("./test_search.db")
            except Exception:
                pass

    def test_adzuna_jooble_mock_fallback(self):
        # Create event loop runner to test async functions
        loop = asyncio.get_event_loop()
        
        # Test Adzuna fallback
        adzuna = AdzunaProvider()
        adzuna_jobs = loop.run_until_complete(adzuna.search("Python"))
        self.assertTrue(len(adzuna_jobs) > 0)
        self.assertEqual(adzuna_jobs[0]["company"], "Stripe")
        
        # Test Jooble fallback
        jooble = JoobleProvider()
        jooble_jobs = loop.run_until_complete(jooble.search("React"))
        self.assertTrue(len(jooble_jobs) > 0)
        self.assertEqual(jooble_jobs[0]["company"], "OpenAI")

    def test_rss_xml_parsing(self):
        sample_rss = """<?xml version="1.0" encoding="utf-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Opportunities</title>
                <item>
                    <title>React Hackathon Challenge</title>
                    <link>https://example.org/hackathon-react</link>
                    <description>Build dynamic UIs with React.</description>
                </item>
                <item>
                    <title>Python Scientific Contest</title>
                    <link>https://example.org/hackathon-python</link>
                    <description>Analyze datasets with pandas and numpy.</description>
                </item>
            </channel>
        </rss>
        """
        provider = RSSProvider()
        results = provider._parse_rss_content(sample_rss, "React", "hackathon", "TestHost")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "React Hackathon Challenge")
        self.assertEqual(results[0]["opportunity_type"], "hackathon")

    def test_aggregator_deduplication(self):
        db = TestingSessionLocal()
        # Seed a job in DB
        existing_job = JobFound(
            title="Senior Developer",
            company="Company A",
            location="Remote",
            description="Testing deduplication",
            url="https://example.com/dedupe-test-job",
            opportunity_type="job"
        )
        db.add(existing_job)
        db.commit()

        # Run aggregator with mock search results containing the seed URL and a new URL
        mock_provider_results = [
            {
                "title": "Senior Developer",
                "company": "Company A",
                "location": "Remote",
                "description": "Testing deduplication",
                "url": "https://example.com/dedupe-test-job",
                "opportunity_type": "job"
            },
            {
                "title": "New Python Engineer",
                "company": "Company B",
                "location": "New York",
                "description": "Fascinating python coding opportunity",
                "url": "https://example.com/new-unique-job",
                "opportunity_type": "job"
            }
        ]

        aggregator = SearchAggregator()
        # Patch the providers list search function to return our custom results
        with patch.object(AdzunaProvider, "search", return_value=mock_provider_results), \
             patch.object(JoobleProvider, "search", return_value=[]), \
             patch.object(GreenhouseProvider, "search", return_value=[]), \
             patch.object(LeverProvider, "search", return_value=[]), \
             patch.object(RSSProvider, "search", return_value=[]):
             
             loop = asyncio.get_event_loop()
             new_inserted = loop.run_until_complete(aggregator.run_aggregation(db, "Python"))
             
             # The existing URL shouldn't be added, only the new one
             self.assertEqual(new_inserted, 1)
             
             # Verify new job is in DB
             db_job = db.query(JobFound).filter(JobFound.url == "https://example.com/new-unique-job").first()
             self.assertIsNotNone(db_job)
             self.assertEqual(db_job.company, "Company B")
        db.close()

    def test_endpoints_flow(self):
        headers = {"Authorization": "Bearer dev-mock-searcher"}
        
        # 1. Trigger search endpoint
        response = self.client.post(
            "/api/v1/search/trigger",
            headers=headers,
            json={"query": "FastAPI", "country": "us"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertTrue(response.json()["new_opportunities_found"] >= 0)
        
        # 2. Query found opportunities
        opps_response = self.client.get(
            "/api/v1/search/opportunities?limit=5",
            headers=headers
        )
        self.assertEqual(opps_response.status_code, 200)
        data = opps_response.json()
        self.assertIn("total", data)
        self.assertIn("items", data)
        self.assertTrue(len(data["items"]) <= 5)

if __name__ == "__main__":
    unittest.main()
