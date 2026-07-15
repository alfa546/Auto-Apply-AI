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
from src.app.models import User, Profile, UserSettings, JobFound, Application
from src.app.services.matching.matcher import MatchingEngine
from src.app.services.matching.pipeline import run_matching_pipeline
from src.app.services.embeddings import generate_and_store_resume_embeddings
from src.app.config import settings

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_matching.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestMatchingAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Override threshold dynamically to tolerate real L2 distances in test
        settings.MATCHING_THRESHOLD = 0.6
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        
        # Seed user, profile, settings, and jobs once
        db = TestingSessionLocal()
        
        user = User(id="matcher_test_uid", email="matcher_test@example.com")
        db.add(user)
        db.commit()
        
        profile = Profile(
            user_id="matcher_test_uid",
            skills=["Python", "FastAPI", "SQL"],
            education=[{"degree": "BS CS", "institution": "Uni", "year": "2020"}],
            experience=[{"title": "SE", "company": "ABC", "description": "Backend dev"}]
        )
        db.add(profile)
        
        user_settings = UserSettings(
            user_id="matcher_test_uid",
            preferred_countries=["Germany", "United Kingdom"],
            min_salary=100000.0,
            remote_preference="remote",
            visa_sponsorship_required=True
        )
        db.add(user_settings)
        db.commit()

        # Seed Vector DB embeddings for the user
        profile_data = {
            "skills": ["Python", "FastAPI", "SQL"],
            "education": [{"degree": "BS CS", "institution": "Uni", "year": "2020"}],
            "experience": [{"title": "SE", "company": "ABC", "description": "Backend dev"}],
            "projects": [],
            "languages": []
        }
        generate_and_store_resume_embeddings("matcher_test_uid", profile_data)

        # Seed Jobs
        cls.job_bad_loc = JobFound(
            title="Python Developer",
            company="Company Bad Loc",
            location="Paris, France",
            description="Looking for Python FastAPI experts.",
            url="https://example.com/bad-loc-job",
            salary="$120,000",
            opportunity_type="job"
        )
        db.add(cls.job_bad_loc)
        
        cls.job_no_visa = JobFound(
            title="FastAPI Engineer",
            company="Company No Visa",
            location="Berlin, Germany",
            description="Looking for Python experts. Visa sponsorship is not available.",
            url="https://example.com/no-visa-job",
            salary="$130,000",
            opportunity_type="job"
        )
        db.add(cls.job_no_visa)

        cls.job_low_salary = JobFound(
            title="Python Developer",
            company="Company Low Pay",
            location="London, United Kingdom",
            description="Looking for Python engineers.",
            url="https://example.com/low-pay-job",
            salary="$80,000",
            opportunity_type="job"
        )
        db.add(cls.job_low_salary)

        cls.job_valid = JobFound(
            title="Senior Python FastAPI Developer",
            company="Perfect Match Corp",
            location="London, United Kingdom",
            description="Fully Remote. Looking for experts in Python and FastAPI. We offer visa sponsorship.",
            url="https://example.com/perfect-match-job",
            salary="$140,000",
            opportunity_type="job"
        )
        db.add(cls.job_valid)
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test_matching.db"):
            try:
                os.remove("./test_matching.db")
            except Exception:
                pass

    def test_matching_engine_hard_constraints(self):
        db = TestingSessionLocal()
        engine_eval = MatchingEngine()
        loop = asyncio.get_event_loop()

        # Retrieve job ids in current session to prevent detached instance errors
        bad_loc_id = db.query(JobFound).filter(JobFound.url == "https://example.com/bad-loc-job").first().id
        no_visa_id = db.query(JobFound).filter(JobFound.url == "https://example.com/no-visa-job").first().id
        low_pay_id = db.query(JobFound).filter(JobFound.url == "https://example.com/low-pay-job").first().id
        valid_id = db.query(JobFound).filter(JobFound.url == "https://example.com/perfect-match-job").first().id

        # Eval Bad Location
        res_loc = loop.run_until_complete(engine_eval.evaluate_job_match(db, "matcher_test_uid", bad_loc_id))
        self.assertFalse(res_loc["is_match"])
        self.assertIn("Location", res_loc["reasons"][0])

        # Eval No Visa
        res_visa = loop.run_until_complete(engine_eval.evaluate_job_match(db, "matcher_test_uid", no_visa_id))
        self.assertFalse(res_visa["is_match"])
        self.assertIn("Visa", res_visa["reasons"][0])

        # Eval Low Salary
        res_sal = loop.run_until_complete(engine_eval.evaluate_job_match(db, "matcher_test_uid", low_pay_id))
        self.assertFalse(res_sal["is_match"])
        self.assertIn("salary", res_sal["reasons"][0].lower())

        # Eval Valid Match
        res_valid = loop.run_until_complete(engine_eval.evaluate_job_match(db, "matcher_test_uid", valid_id))
        self.assertTrue(res_valid["is_match"], msg=str(res_valid))
        self.assertTrue(res_valid["score"] >= 0.6)

        db.close()

    def test_pipeline_execution(self):
        db = TestingSessionLocal()
        loop = asyncio.get_event_loop()
        new_matched = loop.run_until_complete(run_matching_pipeline(db, "matcher_test_uid"))
        
        # Verify it created an application (should match only 1 job - Perfect Match Corp)
        matched_apps = db.query(Application).filter(Application.user_id == "matcher_test_uid").all()
        self.assertEqual(len(matched_apps), 1)
        self.assertEqual(matched_apps[0].company, "Perfect Match Corp")
        self.assertEqual(matched_apps[0].status, "Matched")
        db.close()

    def test_matching_endpoints(self):
        headers = {"Authorization": "Bearer dev-mock-matcher_test_uid"}
        
        # 1. Evaluate single job endpoint
        db = TestingSessionLocal()
        job = db.query(JobFound).filter(JobFound.company == "Perfect Match Corp").first()
        job_id = job.id
        db.close()

        eval_response = self.client.get(
            f"/api/v1/matching/evaluate/{job_id}",
            headers=headers
        )
        self.assertEqual(eval_response.status_code, 200)
        self.assertIn("is_match", eval_response.json())
        self.assertIn("score", eval_response.json())

        # 2. Trigger matching run endpoint (since Perfect Match Corp was already match-registered by the pipeline test,
        # it should run but queue 0 new matches to prevent duplicates).
        response = self.client.post(
            "/api/v1/matching/run",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
