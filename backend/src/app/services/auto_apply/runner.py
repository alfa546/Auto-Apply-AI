import os
import time
import logging
import threading
import uuid
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.app.models import JobFound, Profile, UserSettings, Application
from src.app.services.gmail_client import gmail_client
from src.app.services.llm_client import generate_custom_cover_letter
from src.app.services.application.pipeline import resolve_resume_local_path

logger = logging.getLogger(__name__)

# In-memory batch auto-apply state keyed by user_id
# Structure:
# {
#   "user_id": {
#       "run_id": str,
#       "status": "running" | "completed" | "stopped" | "error",
#       "job_target": int,
#       "job_applied": int,
#       "internship_target": int,
#       "internship_applied": int,
#       "total_applied": int,
#       "total_failed": int,
#       "started_at": float,
#       "completed_at": Optional[float],
#       "last_error": Optional[str],
#       "current_job_title": Optional[str],
#       "current_job_company": Optional[str],
#       "applied_jobs": list[dict],
#   }
# }
_active_runs: Dict[str, dict] = {}
_run_locks: Dict[str, threading.Lock] = {}

class AutoApplyBatchRunner:
    """
    Runs fully automated batch auto-apply in a background thread.
    - Applies to up to `job_count` jobs (max 10)
    - Applies to up to `internship_count` internships (max 3)
    - No per-application user review required (fully autonomous).
    """

    MAX_JOBS = 10
    MAX_INTERNSHIPS = 3

    def start_batch(
        self,
        uid: str,
        user_email: str,
        job_count: int = 10,
        internship_count: int = 3
    ) -> dict:
        """Starts a new auto-apply batch run in the background."""
        # Validate limits
        if job_count < 0 or job_count > self.MAX_JOBS:
            raise ValueError(f"Job count must be between 0 and {self.MAX_JOBS}.")
        if internship_count < 0 or internship_count > self.MAX_INTERNSHIPS:
            raise ValueError(f"Internship count must be between 0 and {self.MAX_INTERNSHIPS}.")
        if job_count == 0 and internship_count == 0:
            raise ValueError("You must set at least 1 job or 1 internship to apply.")

        # Stop previous run if still active
        if uid in _active_runs and _active_runs[uid].get("status") == "running":
            logger.warning(f"User {uid} already has an active auto-apply run. Stopping it first.")
            self.stop_batch(uid)

        run_id = uuid.uuid4().hex[:12]
        state = {
            "run_id": run_id,
            "status": "running",
            "job_target": job_count,
            "job_applied": 0,
            "internship_target": internship_count,
            "internship_applied": 0,
            "total_applied": 0,
            "total_failed": 0,
            "started_at": time.time(),
            "completed_at": None,
            "last_error": None,
            "current_job_title": None,
            "current_job_company": None,
            "applied_jobs": [],
        }
        _active_runs[uid] = state
        _run_locks[uid] = threading.Lock()

        # Launch background thread
        thread = threading.Thread(
            target=self._run_batch_worker,
            args=(uid, user_email, job_count, internship_count, run_id),
            daemon=True,
            name=f"auto-apply-{uid}-{run_id}"
        )
        thread.start()

        logger.info(f"Started auto-apply batch run {run_id} for user {uid}: {job_count} jobs, {internship_count} internships")
        return {
            "success": True,
            "run_id": run_id,
            "message": f"Auto-apply started! Will apply to {job_count} job(s) and {internship_count} internship(s)."
        }

    def stop_batch(self, uid: str) -> dict:
        """Stops the running batch for a user."""
        if uid in _active_runs:
            _active_runs[uid]["status"] = "stopped"
            _active_runs[uid]["completed_at"] = time.time()
            state = _active_runs[uid]
            logger.info(f"Stopped auto-apply run {state['run_id']} for user {uid}")
            return {"success": True, "message": f"Auto-apply stopped. Applied {state['total_applied']} applications so far."}
        return {"success": False, "message": "No active auto-apply run found."}

    def dismiss_batch(self, uid: str) -> dict:
        """Dismisses and clears the stored batch status for a user (only when not running)."""
        if uid in _active_runs and _active_runs[uid].get("status") == "running":
            return {"success": False, "message": "Cannot dismiss an active auto-apply run. Stop it first."}
        if uid in _active_runs:
            _active_runs.pop(uid, None)
            _run_locks.pop(uid, None)
            logger.info(f"Dismissed auto-apply status for user {uid}")
            return {"success": True, "message": "Auto-apply status dismissed."}
        return {"success": True, "message": "No active auto-apply run found."}

    def get_status(self, uid: str) -> dict:
        """Returns current batch status for a user."""
        if uid not in _active_runs:
            return {
                "status": "idle",
                "run_id": None,
                "job_target": 0,
                "job_applied": 0,
                "internship_target": 0,
                "internship_applied": 0,
                "total_applied": 0,
                "total_failed": 0,
                "started_at": None,
                "completed_at": None,
                "current_job_title": None,
                "current_job_company": None,
                "applied_jobs": [],
            }
        # Return a shallow copy so callers cannot mutate internal state
        state = dict(_active_runs[uid])
        state["applied_jobs"] = list(state.get("applied_jobs") or [])
        return state

    def _run_batch_worker(self, uid: str, user_email: str, job_count: int, internship_count: int, run_id: str):
        """Background worker that processes jobs until targets are met or stopped.

        IMPORTANT: Opens its own DB session because the worker runs in a
        background thread and must never share a request-scoped session
        (FastAPI closes those once the HTTP response is sent).
        """
        from src.app.database import SessionLocal

        db = SessionLocal()
        lock = _run_locks.get(uid)
        try:
            # Fetch user profile & settings
            profile = db.query(Profile).filter(Profile.user_id == uid).first()
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()

            if not profile or not profile.resume_url:
                self._update_state(uid, status="error", last_error="User has not uploaded a resume.")
                return

            if not user_settings or not user_settings.is_gmail_connected:
                self._update_state(uid, status="error", last_error="Gmail is not connected.")
                return

            # Resolve resume path once for all sends
            cv_path = resolve_resume_local_path(profile.resume_url)
            if not cv_path or not os.path.exists(cv_path):
                self._update_state(uid, status="error", last_error="Resume file could not be located or downloaded.")
                return

            # Get all available job opportunities, not yet applied to
            applied_urls = set()
            existing_apps = db.query(Application).filter(Application.user_id == uid).all()
            if existing_apps:
                applied_urls = {app.url for app in existing_apps if app.url}

            all_opportunities = db.query(JobFound).order_by(JobFound.found_at.desc()).all()
            job_queue = [o for o in all_opportunities if o.opportunity_type == "job" and o.url not in applied_urls]
            internship_queue = [o for o in all_opportunities if o.opportunity_type == "internship" and o.url not in applied_urls]

            logger.info(f"Auto-apply run {run_id} for user {uid}: {len(job_queue)} jobs available, {len(internship_queue)} internships available")

            # Process jobs first (up to job_target)
            jobs_applied = 0
            for job in job_queue:
                if self._is_stopped(uid):
                    return
                if jobs_applied >= job_count:
                    break

                self._update_state(
                    uid,
                    current_job_title=job.title,
                    current_job_company=job.company
                )

                result = self._auto_apply_one(
                    db=db,
                    uid=uid,
                    user_email=user_email,
                    user_settings=user_settings,
                    profile=profile,
                    job=job,
                    cv_path=cv_path
                )

                if result.get("success"):
                    jobs_applied += 1
                    with lock:
                        _active_runs[uid]["job_applied"] = jobs_applied
                        _active_runs[uid]["total_applied"] += 1
                        _active_runs[uid]["applied_jobs"].append({
                            "title": job.title,
                            "company": job.company,
                            "type": "job",
                            "status": "applied",
                            "recipient": result.get("recipient_email")
                        })
                else:
                    with lock:
                        _active_runs[uid]["total_failed"] += 1
                        _active_runs[uid]["applied_jobs"].append({
                            "title": job.title,
                            "company": job.company,
                            "type": "job",
                            "status": "failed",
                            "error": result.get("error", "Unknown error")
                        })
                    if not result.get("retryable", True):
                        self._update_state(uid, status="error", last_error=result.get("error"))
                        return

                # Small delay between sends to avoid rate limiting
                time.sleep(2)

            # Process internships (up to internship_target)
            internships_applied = 0
            for job in internship_queue:
                if self._is_stopped(uid):
                    return
                if internships_applied >= internship_count:
                    break

                self._update_state(
                    uid,
                    current_job_title=job.title,
                    current_job_company=job.company
                )

                result = self._auto_apply_one(
                    db=db,
                    uid=uid,
                    user_email=user_email,
                    user_settings=user_settings,
                    profile=profile,
                    job=job,
                    cv_path=cv_path
                )

                if result.get("success"):
                    internships_applied += 1
                    with lock:
                        _active_runs[uid]["internship_applied"] = internships_applied
                        _active_runs[uid]["total_applied"] += 1
                        _active_runs[uid]["applied_jobs"].append({
                            "title": job.title,
                            "company": job.company,
                            "type": "internship",
                            "status": "applied",
                            "recipient": result.get("recipient_email")
                        })
                else:
                    with lock:
                        _active_runs[uid]["total_failed"] += 1
                        _active_runs[uid]["applied_jobs"].append({
                            "title": job.title,
                            "company": job.company,
                            "type": "internship",
                            "status": "failed",
                            "error": result.get("error", "Unknown error")
                        })
                    if not result.get("retryable", True):
                        self._update_state(uid, status="error", last_error=result.get("error"))
                        return

                time.sleep(2)

            # Mark completed (if not stopped)
            if not self._is_stopped(uid):
                with lock:
                    _active_runs[uid]["status"] = "completed"
                    _active_runs[uid]["completed_at"] = time.time()
                    _active_runs[uid]["current_job_title"] = None
                    _active_runs[uid]["current_job_company"] = None
                logger.info(f"Auto-apply run {run_id} completed. Total applied: {_active_runs[uid]['total_applied']}")

        except Exception as e:
            logger.error(f"Auto-apply batch worker error for user {uid}: {e}", exc_info=True)
            self._update_state(uid, status="error", last_error=str(e))
        finally:
            try:
                db.close()
            except Exception:
                pass

    def _auto_apply_one(
        self,
        db: Session,
        uid: str,
        user_email: str,
        user_settings: UserSettings,
        profile: Profile,
        job: JobFound,
        cv_path: Optional[str]
    ) -> dict:
        """Sends a single automated application for a job without user review."""
        try:
            recipient_email = job.company_email or f"careers@{job.company.lower().replace(' ', '')}.com"
            sender_email = user_settings.gmail_email_address or user_email
            subject = f"Application for {job.title} - {user_email}"

            # Generate cover letter
            try:
                import src.app.config as config_module
                _saved_openai = config_module.settings.OPENAI_API_KEY
                _saved_gemini = config_module.settings.GEMINI_API_KEY
                if user_settings.openai_api_key:
                    if user_settings.llm_provider == "gemini" or user_settings.openai_api_key.startswith(("AIzaSy", "AQ.")):
                        config_module.settings.GEMINI_API_KEY = user_settings.openai_api_key
                    else:
                        config_module.settings.OPENAI_API_KEY = user_settings.openai_api_key

                try:
                    cover_letter = generate_custom_cover_letter(
                        candidate_name=user_email.split("@")[0],
                        job_title=job.title,
                        company=job.company,
                        skills=profile.skills if profile else [],
                        job_description=job.description or job.title
                    )
                finally:
                    config_module.settings.OPENAI_API_KEY = _saved_openai
                    config_module.settings.GEMINI_API_KEY = _saved_gemini
            except Exception as e:
                logger.warning(f"Cover letter generation fallback for {job.title}: {e}")
                skills_str = ', '.join(profile.skills[:5]) if profile and profile.skills else 'software development'
                cover_letter = (
                    f"Dear Hiring Manager at {job.company},\n\n"
                    f"I am writing to express my strong interest in the {job.title} position.\n"
                    f"With my background in software development and skills in {skills_str}, "
                    f"I am confident in my ability to add immediate value to your team.\n\n"
                    f"Please find my attached resume for your consideration. I look forward to hearing from you.\n\n"
                    f"Best regards,\n{sender_email}"
                )

            # Append profile links
            from src.app.api.auto_apply import build_cover_letter_with_links
            cover_letter = build_cover_letter_with_links(cover_letter, profile)

            # Instant STOP check: do not send email if user clicked stop while LLM was generating
            if self._is_stopped(uid):
                logger.info(f"Auto-apply stopped by user {uid} before email dispatch to {job.company}.")
                return {"success": False, "error": "Stopped by user"}

            # Send email
            if user_settings.smtp_app_password:
                send_result = gmail_client.send_email_via_smtp(
                    sender_email=sender_email,
                    app_password=user_settings.smtp_app_password,
                    recipient_email=recipient_email,
                    subject=subject,
                    body_text=cover_letter,
                    cv_file_path=cv_path
                )
            elif user_settings.gmail_access_token:
                send_result = gmail_client.send_email_via_oauth(
                    access_token=user_settings.gmail_access_token,
                    sender_email=sender_email,
                    recipient_email=recipient_email,
                    subject=subject,
                    body_text=cover_letter,
                    cv_file_path=cv_path,
                    refresh_token=user_settings.gmail_refresh_token,
                    client_id=user_settings.google_client_id,
                    client_secret=user_settings.google_client_secret
                )
                if send_result.get("new_access_token"):
                    user_settings.gmail_access_token = send_result.get("new_access_token")
            else:
                return {"success": False, "error": "No sending method configured.", "retryable": False}

            if not send_result.get("success"):
                return {"success": False, "error": send_result.get("error", "Unknown send error"), "retryable": True}

            # Record application
            app_record = Application(
                user_id=uid,
                title=job.title,
                company=job.company,
                company_email=recipient_email,
                opportunity_type=job.opportunity_type or "job",
                status="Sent via Gmail",
                url=job.url,
                cover_letter=cover_letter,
                notes=f"Auto-apply sent to {recipient_email} via {send_result.get('method')}",
                gmail_message_id=send_result.get("message_id")
            )
            db.add(app_record)
            db.commit()

            logger.info(f"Auto-applied to {job.title} at {job.company} -> {recipient_email}")
            return {"success": True, "recipient_email": recipient_email}

        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            logger.error(f"Auto-apply single job failed for {job.company}: {e}", exc_info=True)
            return {"success": False, "error": str(e), "retryable": True}

    def _update_state(self, uid: str, **kwargs):
        """Thread-safe state update."""
        if uid in _active_runs:
            with _run_locks.get(uid, threading.Lock()):
                for k, v in kwargs.items():
                    _active_runs[uid][k] = v

    def _is_stopped(self, uid: str) -> bool:
        return uid in _active_runs and _active_runs[uid].get("status") == "stopped"


# Singleton instance for the app
auto_apply_runner = AutoApplyBatchRunner()