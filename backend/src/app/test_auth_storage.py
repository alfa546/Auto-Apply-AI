import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.main import app
from src.app.database import Base, get_db
from src.app.models import User, Profile

# Setup a test database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency in app
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestAuthAndStorage(unittest.TestCase):
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
        if os.path.exists("./test_api.db"):
            try:
                os.remove("./test_api.db")
            except Exception:
                pass
        # Clean up any local uploads from the test
        if os.path.exists("uploads"):
            for f in os.listdir("uploads"):
                try:
                    os.remove(os.path.join("uploads", f))
                except Exception:
                    pass

    def test_get_me_unauthorized(self):
        # Without headers, we fallback to mock-user-123 when firebase is not initialized
        response = self.client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "mock-user-123")

    def test_get_me_authorized_mock(self):
        headers = {"Authorization": "Bearer dev-mock-customuser"}
        response = self.client.get("/api/v1/users/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "customuser")

    def test_upload_resume_invalid_format(self):
        headers = {"Authorization": "Bearer dev-mock-uploader"}
        files = {"file": ("resume.txt", b"dummy resume content", "text/plain")}
        response = self.client.post("/api/v1/users/resume", headers=headers, files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Only PDF resume files are accepted", response.json()["detail"])

    def test_upload_resume_valid_pdf(self):
        headers = {"Authorization": "Bearer dev-mock-uploader"}
        files = {"file": ("resume.pdf", b"%PDF-1.4 dummy pdf content", "application/pdf")}
        response = self.client.post("/api/v1/users/resume", headers=headers, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("resume_url", response.json())
        self.assertTrue(response.json()["resume_url"].startswith("/uploads/"))

        # Verify it was updated in the database
        db = TestingSessionLocal()
        user = db.query(User).filter(User.id == "uploader").first()
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.resume_url, response.json()["resume_url"])
        db.close()

if __name__ == "__main__":
    unittest.main()
