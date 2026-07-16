import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.database import Base
from src.app.models import User, Profile, JobFound, Application
from src.app.services.application.pipeline import run_apply_pipeline

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_e2e.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestE2EFlow(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists("./test_e2e.db"):
            try:
                os.remove("./test_e2e.db")
            except Exception:
                pass
        Base.metadata.create_all(bind=engine)
        
        # Create a mock resume file
        cls.resume_temp_path = os.path.abspath("test_resume_mock.pdf")
        with open(cls.resume_temp_path, "w") as f:
            f.write("%PDF-1.4 dummy resume content")
            
        # Seed test data
        cls.db = TestingSessionLocal()
        
        # Create user
        cls.test_user = User(
            id="test-user-id",
            email="testuser@example.com"
        )
        cls.db.add(cls.test_user)
        cls.db.commit()
        
        # Create profile
        cls.test_profile = Profile(
            user_id="test-user-id",
            skills=["Python", "FastAPI", "SQLAlchemy"],
            experience=[{"title": "Software Engineer", "company": "Tech Corp", "duration": "2 years"}],
            education=[{"degree": "BS CS", "institution": "State University", "year": "2022"}],
            resume_url="/uploads/test_resume.pdf"
        )
        cls.db.add(cls.test_profile)
        
        # Create job
        cls.test_job = JobFound(
            id=101,
            title="Python Developer",
            company="Innovate LLC",
            url="https://innovate.example.com/apply/python-dev",
            description="We are looking for a Python Developer experienced in FastAPI.",
            opportunity_type="job"
        )
        cls.db.add(cls.test_job)
        cls.db.commit()

        # Create application tracking entry
        cls.test_application = Application(
            id=202,
            user_id="test-user-id",
            title="Python Developer",
            company="Innovate LLC",
            url="https://innovate.example.com/apply/python-dev",
            status="Matched",
            notes="Ready to apply"
        )
        cls.db.add(cls.test_application)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test_e2e.db"):
            try:
                os.remove("./test_e2e.db")
            except Exception:
                pass
        if os.path.exists("./test_resume_mock.pdf"):
            try:
                os.remove("./test_resume_mock.pdf")
            except Exception:
                pass

    @patch("src.app.services.application.pipeline.resolve_resume_local_path")
    @patch("src.app.services.application.pipeline.extract_text_from_pdf")
    @patch("src.app.services.application.pipeline.generate_cover_letter")
    @patch("src.app.services.application.form_filler.FormFillerService.auto_fill_application")
    @patch("src.app.services.notification.NotificationService.send_notification")
    async def test_successful_apply_pipeline_e2e(self, mock_send_notification, mock_auto_fill, mock_cover_letter, mock_extract, mock_resolve):
        # Configure mocks
        mock_resolve.return_value = self.resume_temp_path
        mock_extract.return_value = "Candidate Resume Text\nPhone: 1234567890"
        mock_cover_letter.return_value = "Mocked cover letter body"
        mock_auto_fill.return_value = {"success": True, "screenshot_path": "/uploads/screenshot_123.png"}
        mock_send_notification.return_value = {"discord": True, "telegram": True}

        # Run pipeline
        res = await run_apply_pipeline(self.db, "test-user-id", 202)

        # Assertions
        self.assertTrue(res["success"])
        self.assertEqual(res["screenshot_path"], "/uploads/screenshot_123.png")

        # Verify DB updates
        app_record = self.db.query(Application).filter(Application.id == 202).first()
        self.assertEqual(app_record.status, "Applied")
        self.assertIn("screenshot_123.png", app_record.notes)
        self.assertEqual(app_record.cover_letter, "Mocked cover letter body")

        # Verify notification was dispatched
        mock_send_notification.assert_called_once()
        notification_text = mock_send_notification.call_args[0][0]
        self.assertIn("Successfully applied to", notification_text)
        self.assertIn("Python Developer", notification_text)

    @patch("src.app.services.application.pipeline.resolve_resume_local_path")
    @patch("src.app.services.application.pipeline.extract_text_from_pdf")
    @patch("src.app.services.application.pipeline.generate_cover_letter")
    @patch("src.app.services.application.form_filler.FormFillerService.auto_fill_application")
    @patch("src.app.services.notification.NotificationService.send_notification")
    async def test_failed_apply_pipeline_e2e(self, mock_send_notification, mock_auto_fill, mock_cover_letter, mock_extract, mock_resolve):
        # Set application status back to Matched for failure test
        app_record = self.db.query(Application).filter(Application.id == 202).first()
        app_record.status = "Matched"
        self.db.commit()

        # Configure mocks to return failure
        mock_resolve.return_value = self.resume_temp_path
        mock_extract.return_value = "Candidate Resume Text\nPhone: 1234567890"
        mock_cover_letter.return_value = "Mocked cover letter body"
        mock_auto_fill.return_value = {"success": False, "error_message": "Form submission timeout"}
        mock_send_notification.return_value = {"discord": True, "telegram": True}

        # Run pipeline
        res = await run_apply_pipeline(self.db, "test-user-id", 202)

        # Assertions
        self.assertFalse(res["success"])
        self.assertEqual(res["error_message"], "Form submission timeout")

        # Verify DB updates
        app_record = self.db.query(Application).filter(Application.id == 202).first()
        self.assertEqual(app_record.status, "Failed")
        self.assertIn("Form submission timeout", app_record.notes)

        # Verify notification was dispatched
        mock_send_notification.assert_called_once()
        notification_text = mock_send_notification.call_args[0][0]
        self.assertIn("Failed to apply to", notification_text)
        self.assertIn("Form submission timeout", notification_text)

if __name__ == "__main__":
    unittest.main()
