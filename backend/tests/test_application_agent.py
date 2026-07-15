import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
import asyncio
import http.server
import socketserver
import threading
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.main import app
from src.app.database import Base, get_db
from src.app.models import User, Profile, UserSettings, JobFound, Application
from src.app.services.application.cover_letter import generate_cover_letter
from src.app.services.application.form_filler import FormFillerService
from src.app.services.application.pipeline import run_apply_pipeline

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_application.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock HTTP Form Server for Playwright testing
class MockFormHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <html>
        <head><title>Mock Job Board Form</title></head>
        <body>
            <form id="app-form" method="POST" action="/submit" enctype="multipart/form-data">
                <label for="first_name">First Name</label>
                <input type="text" id="first_name" name="first_name" placeholder="John" /><br/>
                
                <label for="last_name">Last Name</label>
                <input type="text" id="last_name" name="last_name" /><br/>
                
                <label for="email">Email</label>
                <input type="email" id="email" name="email" /><br/>
                
                <label for="phone">Phone</label>
                <input type="tel" id="phone" name="phone" /><br/>
                
                <label for="resume">Upload Resume</label>
                <input type="file" id="resume" name="resume" /><br/>
                
                <label for="cover_letter">Cover Letter Details</label>
                <textarea id="cover_letter" name="cover_letter"></textarea><br/>
                
                <input type="submit" id="submit_app" value="Submit Application" />
            </form>
            <div id="success-msg" style="display:none;">Application Submitted Successfully!</div>
            <script>
                document.getElementById('app-form').addEventListener('submit', function(e) {
                    e.preventDefault();
                    document.getElementById('app-form').style.display = 'none';
                    document.getElementById('success-msg').style.display = 'block';
                });
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        # Mute logging outputs in pytest output
        pass

def start_mock_server():
    httpd = socketserver.TCPServer(("127.0.0.1", 0), MockFormHandler)
    port = httpd.socket.getsockname()[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port

class TestApplicationAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.dependency_overrides[get_db] = override_get_db
        # Redirect SessionLocal in database module to SQLite testing engine
        import src.app.database
        cls.original_session_local = src.app.database.SessionLocal
        src.app.database.SessionLocal = TestingSessionLocal
        
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        
        # Start mock server
        cls.server, cls.port = start_mock_server()
        
        # Create a mock resume file
        cls.resume_temp_path = os.path.abspath("test_resume_mock.pdf")
        with open(cls.resume_temp_path, "w") as f:
            f.write("%PDF-1.4 dummy resume content")

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        # Restore SessionLocal
        import src.app.database
        src.app.database.SessionLocal = cls.original_session_local
        
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        
        # Stop mock server
        cls.server.shutdown()
        cls.server.server_close()
        
        # Cleanup mock DB and mock resume
        if os.path.exists("./test_application.db"):
            try:
                os.remove("./test_application.db")
            except Exception:
                pass
        if os.path.exists(cls.resume_temp_path):
            try:
                os.remove(cls.resume_temp_path)
            except Exception:
                pass
        # Clean up screenshots folder
        if os.path.exists("uploads/screenshots"):
            for f in os.listdir("uploads/screenshots"):
                try:
                    os.remove(os.path.join("uploads/screenshots", f))
                except Exception:
                    pass

    def test_cover_letter_generator_template(self):
        profile = {
            "skills": ["React", "FastAPI"],
            "experience": [{"title": "Eng", "company": "Stripe", "description": "built APIs"}],
            "education": [{"degree": "BSc", "institution": "Stanford", "year": "2020"}]
        }
        cl = generate_cover_letter(profile, "Python Developer", "OpenAI", "Need python developer")
        self.assertIn("Python Developer", cl)
        self.assertIn("OpenAI", cl)
        self.assertIn("Stripe", cl)

    def test_playwright_form_filler(self):
        url = f"http://127.0.0.1:{self.port}/"
        candidate = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "123-456-7890",
            "linkedin": "https://linkedin.com/in/janedoe",
            "github": "https://github.com/janedoe"
        }
        cover_letter = "This is my cover letter."

        loop = asyncio.get_event_loop()
        filler = FormFillerService()
        result = loop.run_until_complete(
            filler.auto_fill_application(
                application_url=url,
                candidate_info=candidate,
                resume_path=self.resume_temp_path,
                cover_letter_content=cover_letter
            )
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["screenshot_path"])
        self.assertTrue(result["screenshot_path"].startswith("/uploads/screenshots/"))

    @patch("src.app.services.application.pipeline.extract_text_from_pdf")
    def test_apply_pipeline_and_endpoints(self, mock_extract):
        mock_extract.return_value = "Mocked Resume Text: skills: Python, Playwright"
        db = TestingSessionLocal()
        
        # 1. Setup User & Profile details
        user = User(id="apply_test_uid", email="apply_test@example.com")
        db.add(user)
        db.commit()

        profile = Profile(
            user_id="apply_test_uid",
            skills=["Python", "Playwright"],
            resume_url=self.resume_temp_path
        )
        db.add(profile)
        
        # 2. Setup job opportunity
        job = JobFound(
            title="Automation Engineer",
            company="Mocking Corp",
            location="Remote",
            description="We want Playwright automation experts.",
            url=f"http://127.0.0.1:{self.port}/",
            opportunity_type="job"
        )
        db.add(job)
        db.commit()

        # 3. Setup application item
        app_item = Application(
            user_id="apply_test_uid",
            title="Automation Engineer",
            company="Mocking Corp",
            opportunity_type="job",
            status="Matched",
            url=f"http://127.0.0.1:{self.port}/"
        )
        db.add(app_item)
        db.commit()

        # 4. Trigger pipeline
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(run_apply_pipeline(db, "apply_test_uid", app_item.id))
        self.assertTrue(res["success"])
        self.assertEqual(app_item.status, "Applied")
        db.close()

        # 5. Check endpoints API
        headers = {"Authorization": "Bearer dev-mock-apply_test_uid"}
        
        # Get applications list
        list_resp = self.client.get("/api/v1/applications", headers=headers)
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(len(list_resp.json()) > 0)
        self.assertEqual(list_resp.json()[0]["status"], "Applied")

        # Get details
        app_id = list_resp.json()[0]["id"]
        detail_resp = self.client.get(f"/api/v1/applications/{app_id}", headers=headers)
        self.assertEqual(detail_resp.status_code, 200)
        self.assertEqual(detail_resp.json()["company"], "Mocking Corp")

        # Trigger re-apply POST endpoint
        # Set status back to Matched
        db = TestingSessionLocal()
        app_db = db.query(Application).filter(Application.id == app_id).first()
        app_db.status = "Matched"
        db.commit()
        db.close()

        trigger_resp = self.client.post(f"/api/v1/applications/{app_id}/apply", headers=headers)
        self.assertEqual(trigger_resp.status_code, 200)
        self.assertEqual(trigger_resp.json()["status"], "queued")

if __name__ == "__main__":
    unittest.main()
