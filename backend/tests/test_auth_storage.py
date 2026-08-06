import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        # Without valid JWT token headers, endpoint correctly rejects with 401 Unauthorized
        response = self.client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Missing authentication credentials", response.json()["detail"])

    def test_get_me_authorized_mock(self):
        # Create test user in DB and override auth dependency
        db = TestingSessionLocal()
        test_user = User(id="customuser", email="custom@example.com", is_active=True)
        db.merge(test_user)
        db.commit()
        db.close()

        from src.app.auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: test_user

        response = self.client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "customuser")
        app.dependency_overrides.pop(get_current_user, None)

    def test_upload_resume_invalid_format(self):
        db = TestingSessionLocal()
        uploader = User(id="uploader", email="uploader@example.com", is_active=True)
        db.merge(uploader)
        db.commit()
        db.close()

        from src.app.auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: uploader

        files = {"file": ("resume.txt", b"dummy resume content", "text/plain")}
        response = self.client.post("/api/v1/users/resume", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Only PDF resume files are accepted", response.json()["detail"])
        app.dependency_overrides.pop(get_current_user, None)

    def test_upload_resume_valid_pdf(self):
        db = TestingSessionLocal()
        uploader = User(id="uploader", email="uploader@example.com", is_active=True)
        db.merge(uploader)
        db.commit()
        db.close()

        from src.app.auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: uploader

        files = {"file": ("resume.pdf", b"%PDF-1.4 dummy pdf content", "application/pdf")}
        response = self.client.post("/api/v1/users/resume", files=files)
        self.assertEqual(response.status_code, 200)
        self.assertIn("resume_url", response.json())
        self.assertTrue(response.json()["resume_url"].startswith("/uploads/"))
        app.dependency_overrides.pop(get_current_user, None)

        # Verify it was updated in the database
        db = TestingSessionLocal()
        user = db.query(User).filter(User.id == "uploader").first()
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.resume_url, response.json()["resume_url"])
        db.close()

if __name__ == "__main__":
    unittest.main()
