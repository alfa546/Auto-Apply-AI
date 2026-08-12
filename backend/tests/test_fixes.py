"""
Regression tests for backend robustness fixes.
Run from the backend directory:  python -m pytest tests/test_fixes.py -v
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestLLMProviderDetection(unittest.TestCase):
    """detect_llm_provider must recognise all modern key formats."""

    def test_legacy_gemini_key(self):
        from src.app.services.llm_client import detect_llm_provider

        self.assertEqual(detect_llm_provider("AIzaSyabc123"), "gemini")

    def test_new_google_aq_prefixed_key(self):
        # New 2025+ Google/Gemini key format was previously misclassified
        # as "invalid", silently disabling every LLM feature.
        from src.app.services.llm_client import detect_llm_provider

        self.assertEqual(detect_llm_provider("AQ.Ab8RN6LCEEDueCRhpAOmN4d8r1FIs7YdilwpWTy8ob7V8MOOwkA"), "gemini")
        self.assertNotEqual(detect_llm_provider("AQ.xxx"), "invalid")

    def test_openai_and_anthropic_keys(self):
        from src.app.services.llm_client import detect_llm_provider

        self.assertEqual(detect_llm_provider("sk-proj-abc123"), "openai")
        self.assertEqual(detect_llm_provider("sk-ant-api03-xyz"), "anthropic")
        self.assertEqual(detect_llm_provider("gsk_abc"), "groq")


class TestConfigListParsing(unittest.TestCase):
    """CORS_ORIGINS / ALLOWED_HOSTS must never crash on plain strings."""

    def test_normalize_str_list_accepts_all_formats(self):
        from src.app.config import _normalize_str_list

        self.assertEqual(_normalize_str_list("https://a.com,https://b.com"), ["https://a.com", "https://b.com"])
        self.assertEqual(_normalize_str_list('["https://a.com", "https://b.com"]'), ["https://a.com", "https://b.com"])
        self.assertEqual(_normalize_str_list("https://a.com"), ["https://a.com"])
        self.assertEqual(_normalize_str_list(None), [])
        self.assertEqual(_normalize_str_list(["x", "  y "]), ["x", "y"])

    def test_settings_load_with_string_env(self):
        # Regression: setting CORS_ORIGINS as a plain string used to crash
        # the entire process with pydantic_settings.SettingsError.
        import os
        import src.app.config as config

        previous = os.environ.get("CORS_ORIGINS")
        previous_hosts = os.environ.get("ALLOWED_HOSTS")
        try:
            os.environ["CORS_ORIGINS"] = "https://a.com,https://b.com"
            os.environ["ALLOWED_HOSTS"] = "api.example.com,localhost"
            s = config.Settings(_env_file=None)
            self.assertEqual(s.CORS_ORIGINS, ["https://a.com", "https://b.com"])
            self.assertEqual(s.ALLOWED_HOSTS, ["api.example.com", "localhost"])
        finally:
            if previous is None:
                os.environ.pop("CORS_ORIGINS", None)
            else:
                os.environ["CORS_ORIGINS"] = previous
            if previous_hosts is None:
                os.environ.pop("ALLOWED_HOSTS", None)
            else:
                os.environ["ALLOWED_HOSTS"] = previous_hosts


class TestAuthValidators(unittest.TestCase):
    def test_password_minimum_length(self):
        from src.app.api.auth import UserCreate

        with self.assertRaises(Exception):
            UserCreate(email="user@example.com", password="short")

        valid = UserCreate(email="User@Example.COM", password="supersecret123")
        # Emails are normalized to lowercase
        self.assertEqual(valid.email, "user@example.com")
        self.assertEqual(valid.password, "supersecret123")


class TestFallbackRecipientEmail(unittest.TestCase):
    def test_sanitize_company_domain(self):
        from src.app.api.auto_apply import sanitize_company_domain, build_fallback_recipient_email

        self.assertEqual(sanitize_company_domain("Acme Corporation"), "acmecorporation")
        self.assertEqual(build_fallback_recipient_email("Acme Corp"), "careers@acmecorp.com")
        # Company names never produce broken domains
        self.assertNotIn(" ", build_fallback_recipient_email("Acme Corporation"))
        self.assertEqual(build_fallback_recipient_email(""), "")
        self.assertEqual(build_fallback_recipient_email("X"), "")
class TestAutoApplyRunnerState(unittest.TestCase):
    def setUp(self):
        from src.app.services.auto_apply.runner import AutoApplyBatchRunner, _active_runs, _run_locks

        self.runner = AutoApplyBatchRunner()
        self._active_runs = _active_runs
        self._run_locks = _run_locks
        # Clear any leftover state
        self._active_runs.clear()
        self._run_locks.clear()

    def test_start_batch_validates_limits(self):
        with self.assertRaises(ValueError):
            self.runner.start_batch(uid="u1", user_email="a@b.com", job_count=99)
        with self.assertRaises(ValueError):
            self.runner.start_batch(uid="u1", user_email="a@b.com", internship_count=20)
        with self.assertRaises(ValueError):
            self.runner.start_batch(uid="u1", user_email="a@b.com", job_count=0, internship_count=0)

    def test_get_status_returns_idle_and_copy(self):
        status = self.runner.get_status("nosuchuser")
        self.assertEqual(status["status"], "idle")

        # A returned dict must be a copy - mutations must not corrupt internal state
        self._active_runs["user1"] = {"status": "completed", "applied_jobs": [{"title": "x"}]}
        state = self.runner.get_status("user1")
        self.assertEqual(state["status"], "completed")
        state["status"] = "hacked"
        state["applied_jobs"].append("junk")
        self.assertEqual(self._active_runs["user1"]["status"], "completed")
        self.assertEqual(len(self._active_runs["user1"]["applied_jobs"]), 1)

    def test_dismiss_running_run_blocked(self):
        self._active_runs["user2"] = {"status": "running"}
        result = self.runner.dismiss_batch("user2")
        self.assertFalse(result["success"])
        self.assertIn("Stop it first", result["message"])

    def test_dismiss_completed_run(self):
        self._active_runs["user3"] = {"status": "completed"}
        result = self.runner.dismiss_batch("user3")
        self.assertTrue(result["success"])
        self.assertNotIn("user3", self._active_runs)


if __name__ == "__main__":
    unittest.main()