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
from src.app.models import User, Profile, Application, EmailInteraction
from src.app.services.email.watcher import EmailInboxWatcher
from src.app.services.email.classifier import classify_email
from src.app.services.email.draft_writer import generate_draft_reply

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_email.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock IMAP Connection
class MockIMAPConnection:
    def __init__(self, *args, **kwargs):
        pass
    def login(self, username, password):
        pass
    def select(self, folder):
        return "OK", b"1"
    def search(self, charset, criteria):
        return "OK", [b"1 2"]
    def fetch(self, message_set, message_parts):
        email_1 = b"""From: Google Recruiter <recruiter@google.com>
To: email_test@example.com
Subject: Google Interview Invitation
Content-Type: text/plain

Hi Candidate,
We would love to schedule a video interview with you. Please let us know your availability.
"""
        email_2 = b"""From: Stripe Team <jobs@stripe.com>
To: email_test@example.com
Subject: Update on your Stripe application
Content-Type: text/plain

Hi Candidate,
Thank you for your interest. Unfortunately, we are not moving forward with your application.
"""
        if message_set == b"1":
            return "OK", [(None, email_1)]
        else:
            return "OK", [(None, email_2)]
    def close(self):
        pass
    def logout(self):
        pass

class TestEmailAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        # Redirect SessionLocal in database module to SQLite testing engine
        import src.app.database
        cls.original_session_local = src.app.database.SessionLocal
        src.app.database.SessionLocal = TestingSessionLocal
        
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        # Restore SessionLocal
        import src.app.database
        src.app.database.SessionLocal = cls.original_session_local
        
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test_email.db"):
            try:
                os.remove("./test_email.db")
            except Exception:
                pass

    def test_email_classification(self):
        # Test Interview Invite classification
        res_invite = classify_email("Invitation to speak with Stripe", "We would love to schedule a video interview.")
        self.assertEqual(res_invite, "Interview Invite")

        # Test Rejection classification
        res_reject = classify_email("Stripe Application Update", "Unfortunately, we decided to pursue other candidates.")
        self.assertEqual(res_reject, "Rejection")

    def test_draft_writer(self):
        profile = {"name": "Alex", "skills": ["Python"]}
        
        # Invite draft
        draft_invite = generate_draft_reply("Interview Invite", "recruiter@google.com", "Google Call", "schedule interview", profile)
        self.assertIn("Alex", draft_invite)
        self.assertIn("schedule", draft_invite.lower())

        # Rejection draft
        draft_reject = generate_draft_reply("Rejection", "recruiter@google.com", "Google Application", "not moving forward", profile)
        self.assertIn("Alex", draft_reject)
        self.assertIn("stay in touch", draft_reject.lower())

    @patch("src.app.services.email.watcher.settings")
    @patch("imaplib.IMAP4_SSL")
    def test_inbox_watcher_and_endpoints(self, mock_imap_class, mock_settings):
        # 1. Setup credentials to bypass configuration guard
        mock_settings.EMAIL_IMAP_SERVER = "imap.example.com"
        mock_settings.EMAIL_ADDRESS = "email_test@example.com"
        mock_settings.EMAIL_PASSWORD = "appsecretpassword"
        
        # Instantiating mock connection
        mock_imap_class.return_value = MockIMAPConnection()

        db = TestingSessionLocal()
        
        # Seed User
        user = User(id="email_test_uid", email="email_test@example.com")
        db.add(user)
        db.commit()

        # Seed User Applications (Google and Stripe) so the watcher filters them in
        app_google = Application(
            user_id="email_test_uid",
            title="Software Developer",
            company="Google",
            status="Applied"
        )
        app_stripe = Application(
            user_id="email_test_uid",
            title="Software Developer",
            company="Stripe",
            status="Applied"
        )
        db.add(app_google)
        db.add(app_stripe)
        db.commit()

        # 2. Test Watcher checks
        watcher = EmailInboxWatcher()
        loop = asyncio.get_event_loop()
        matches = loop.run_until_complete(watcher.check_inbox(db, "email_test_uid"))
        
        # Must find 2 matched emails (Google and Stripe)
        self.assertEqual(len(matches), 2)
        self.assertTrue(any(m["company"] == "Google" for m in matches))
        self.assertTrue(any(m["company"] == "Stripe" for m in matches))
        db.close()

        # 3. Test API Endpoints
        headers = {"Authorization": "Bearer dev-mock-email_test_uid"}
        
        # Trigger manual check POST endpoint
        check_resp = self.client.post("/api/v1/emails/check", headers=headers)
        self.assertEqual(check_resp.status_code, 200)
        self.assertEqual(check_resp.json()["status"], "success")

        # Give background tasks a brief moment to run (since TestClient runs them synchronously, they complete immediately)
        # Verify drafts are fetched via GET endpoint
        drafts_resp = self.client.get("/api/v1/emails/drafts", headers=headers)
        self.assertEqual(drafts_resp.status_code, 200)
        drafts = drafts_resp.json()
        
        # Assert database saved 2 drafts (one invite, one rejection)
        self.assertEqual(len(drafts), 2)
        
        # Find Google draft
        google_draft = next(d for d in drafts if "Google" in d["sender"] or "Google" in d["subject"])
        self.assertEqual(google_draft["classification"], "Interview Invite")
        self.assertEqual(google_draft["status"], "Pending Review")

        # Approve Google draft
        approve_resp = self.client.post(f"/api/v1/emails/drafts/{google_draft['id']}/approve", headers=headers)
        self.assertEqual(approve_resp.status_code, 200)
        
        # Verify status updated
        updated_resp = self.client.get("/api/v1/emails/drafts", headers=headers)
        google_draft_updated = next(d for d in updated_resp.json() if d["id"] == google_draft["id"])
        self.assertEqual(google_draft_updated["status"], "Approved")

        # Discard Stripe draft
        stripe_draft = next(d for d in drafts if "Stripe" in d["sender"] or "Stripe" in d["subject"])
        discard_resp = self.client.delete(f"/api/v1/emails/drafts/{stripe_draft['id']}", headers=headers)
        self.assertEqual(discard_resp.status_code, 200)

        # Verify status updated to Dismissed
        updated_resp_2 = self.client.get("/api/v1/emails/drafts", headers=headers)
        stripe_draft_updated = next(d for d in updated_resp_2.json() if d["id"] == stripe_draft["id"])
        self.assertEqual(stripe_draft_updated["status"], "Dismissed")

if __name__ == "__main__":
    unittest.main()
