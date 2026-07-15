import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.main import app
from src.app.database import Base, get_db
from src.app.models import User, Profile
from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.resume_parser import parse_resume_text
from src.app.services.ats_checker import evaluate_resume_ats
from src.app.services.embeddings import generate_embeddings, generate_and_store_resume_embeddings

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_resume.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestResumeAgent(unittest.TestCase):
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
        if os.path.exists("./test_resume.db"):
            try:
                os.remove("./test_resume.db")
            except Exception:
                pass
        if os.path.exists("uploads"):
            for f in os.listdir("uploads"):
                try:
                    os.remove(os.path.join("uploads", f))
                except Exception:
                    pass

    def test_pdf_extraction_fallback(self):
        # Verify value error is raised for completely corrupt non-PDF content.
        with self.assertRaises(ValueError):
            extract_text_from_pdf(b"corrupt non pdf data")

    def test_rule_based_parser_fallback(self):
        sample_text = """
        John Doe
        Email: john@example.com
        
        # EXPERIENCE
        Software Developer at ABC Corp
        Developed Python web apps using Django and FastAPI.
        
        # SKILLS
        Python, JavaScript, SQL, Git, Docker
        
        # EDUCATION
        BS in Computer Science from Stanford University (2020)
        
        # PROJECTS
        Personal Website - portfolio built in React
        
        # LANGUAGES
        English, Spanish
        """
        parsed = parse_resume_text(sample_text)
        self.assertIn("Python", parsed["skills"])
        self.assertIn("JavaScript", parsed["skills"])
        self.assertTrue(len(parsed["experience"]) > 0)
        self.assertTrue(len(parsed["education"]) > 0)
        self.assertTrue(len(parsed["projects"]) > 0)
        self.assertIn("English", parsed["languages"])

    def test_ats_checker_rule_based(self):
        profile = {
            "skills": ["Python", "Docker", "Git", "FastAPI"],
            "experience": [{"title": "Dev", "company": "Co", "description": "Short desc"}],
            "education": [{"degree": "BSc", "institution": "Uni", "year": "2020"}],
            "projects": [],
            "languages": ["English"]
        }
        res = evaluate_resume_ats(profile, target_role="Python Developer")
        self.assertIn("ats_score", res)
        self.assertIn("ats_suggestions", res)
        self.assertTrue(res["ats_score"] >= 30 and res["ats_score"] <= 100)

    def test_embeddings_generation_fallback(self):
        # Verify generate_embeddings returns the correct dimensions even in fallback
        vectors = generate_embeddings(["hello world", "test text"])
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 384)

    @patch("src.app.api.users.extract_text_from_pdf")
    def test_api_upload_parse_profile_flow(self, mock_extract):
        mock_extract.return_value = """
        # SKILLS
        Python, React
        # EDUCATION
        BSc Computer Science
        # EXPERIENCE
        Dev at Startup
        """
        headers = {"Authorization": "Bearer dev-mock-tester"}
        files = {"file": ("my_resume.pdf", b"%PDF-1.4 mock pdf content", "application/pdf")}
        
        # Upload
        response = self.client.post("/api/v1/users/resume", headers=headers, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("resume_url", response.json())
        
        # Fetch Profile
        profile_resp = self.client.get("/api/v1/resumes/profile", headers=headers)
        self.assertEqual(profile_resp.status_code, 200)
        data = profile_resp.json()
        self.assertIn("Python", data["skills"])
        self.assertIn("ats_score", data)
        self.assertIsNotNone(data["ats_score"])
        
        # Run ad-hoc ATS check
        ats_check_resp = self.client.post(
            "/api/v1/resumes/ats-check",
            headers=headers,
            json={"target_role": "React Developer"}
        )
        self.assertEqual(ats_check_resp.status_code, 200)
        self.assertIn("ats_score", ats_check_resp.json())

if __name__ == "__main__":
    unittest.main()
