import os
import base64
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional, Dict, Any

from src.app.config import settings

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def get_authorization_url(self, user_id: str, client_id: Optional[str] = None) -> str:
        """
        Generate Google OAuth2 Authorization URL.
        """
        cid = client_id or self.client_id
        if not cid:
            # Fallback mock OAuth URL for testing / dev mode
            return f"{settings.FRONTEND_BASE_URL}?gmail_connected=true&mock=true&state={user_id}"
            
        scopes = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/userinfo.email",
        ]
        from urllib.parse import urlencode
        params = {
            "client_id": cid,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": user_id,
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def exchange_code_for_tokens(self, code: str, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchanges Google OAuth authorization code for access_token and refresh_token.
        """
        import httpx
        cid = client_id or self.client_id
        csecret = client_secret or self.client_secret
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": cid,
            "client_secret": csecret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, data=payload)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "success": True,
                        "access_token": data.get("access_token"),
                        "refresh_token": data.get("refresh_token"),
                        "expires_in": data.get("expires_in")
                    }
                else:
                    logger.error(f"OAuth token exchange error: {res.text}")
                    return {"success": False, "error": res.text}
        except Exception as e:
            logger.error(f"OAuth token exchange exception: {e}")
            return {"success": False, "error": str(e)}

    def refresh_access_token(self, refresh_token: str, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Dict[str, Any]:
        """
        Refresh Google OAuth2 Access Token using the refresh token.
        Uses user-provided client_id/client_secret if available, otherwise falls back to global config.
        """
        import httpx
        cid = client_id or self.client_id
        csecret = client_secret or self.client_secret
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": cid,
            "client_secret": csecret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, data=payload)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "success": True,
                        "access_token": data.get("access_token"),
                        "expires_in": data.get("expires_in")
                    }
                else:
                    logger.error(f"OAuth token refresh error: {res.text}")
                    return {"success": False, "error": res.text}
        except Exception as e:
            logger.error(f"OAuth token refresh exception: {e}")
            return {"success": False, "error": str(e)}

    def create_mime_message(
        self,
        sender_email: str,
        recipient_email: str,
        subject: str,
        body_text: str,
        cv_file_path: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Construct an RFC 2822 MIME Email Message with Cover Letter and attached CV PDF.
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach Cover Letter body text
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

        # Attach CV PDF file if present
        if cv_file_path and os.path.exists(cv_file_path):
            try:
                filename = os.path.basename(cv_file_path)
                with open(cv_file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
                logger.info(f"Attached CV file '{filename}' to email for {recipient_email}")
            except Exception as e:
                logger.error(f"Error attaching CV file to email: {e}")

        return msg

    def send_email_via_smtp(
        self,
        sender_email: str,
        app_password: str,
        recipient_email: str,
        subject: str,
        body_text: str,
        cv_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using Gmail SMTP with App Password.
        """
        from src.app.services.email.queue import email_rate_limiter
        if not email_rate_limiter.can_send():
            logger.warning("Email rate limit exceeded (SMTP).")
            return {"success": False, "error": "Email rate limit exceeded. Please try again later."}

        try:
            msg = self.create_mime_message(sender_email, recipient_email, subject, body_text, cv_file_path)
            
            with smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                
            email_rate_limiter.record_send()
            logger.info(f"Email successfully sent via SMTP to {recipient_email}")
            import uuid
            return {
                "success": True,
                "message_id": f"smtp_{uuid.uuid4().hex[:12]}",
                "method": "SMTP"
            }
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return {"success": False, "error": str(e)}

    def send_email_via_oauth(
        self,
        access_token: str,
        sender_email: str,
        recipient_email: str,
        subject: str,
        body_text: str,
        cv_file_path: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using Google Gmail API with OAuth2 Access Token.
        """
        from src.app.services.email.queue import email_rate_limiter
        if not email_rate_limiter.can_send():
            logger.warning("Email rate limit exceeded (OAuth).")
            return {"success": False, "error": "Email rate limit exceeded. Please try again later."}

        try:
            import httpx
            msg = self.create_mime_message(sender_email, recipient_email, subject, body_text, cv_file_path)
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            payload = {"raw": raw_message}
            
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, json=payload, headers=headers)
                
                if res.status_code == 401 and refresh_token:
                    logger.info("Access token expired, attempting to refresh...")
                    refresh_result = self.refresh_access_token(refresh_token, client_id=client_id, client_secret=client_secret)
                    if refresh_result.get("success"):
                        new_access_token = refresh_result.get("access_token")
                        headers["Authorization"] = f"Bearer {new_access_token}"
                        res = client.post(url, json=payload, headers=headers)
                        if res.status_code == 200:
                            email_rate_limiter.record_send()
                            data = res.json()
                            return {
                                "success": True,
                                "message_id": data.get("id"),
                                "thread_id": data.get("threadId"),
                                "method": "Gmail_OAuth",
                                "new_access_token": new_access_token
                            }
                        else:
                            # Return new access token even if send failed, so it can be saved for next attempt
                            logger.error(f"Gmail API error after token refresh: {res.status_code} - {res.text}")
                            return {"success": False, "error": res.text, "new_access_token": new_access_token}

                if res.status_code == 200:
                    email_rate_limiter.record_send()
                    data = res.json()
                    return {
                        "success": True,
                        "message_id": data.get("id"),
                        "thread_id": data.get("threadId"),
                        "method": "Gmail_OAuth"
                    }
                elif res.status_code == 403:
                    # Gmail API not enabled in the Google Cloud project
                    error_msg = (
                        "Gmail API is not enabled for this Google Cloud project. "
                        "Please enable it at https://console.developers.google.com/apis/api/gmail.googleapis.com "
                        "or use SMTP App Password instead. "
                        f"Details: {res.text}"
                    )
                    logger.error(f"Gmail API 403 (not enabled): {error_msg}")
                    return {"success": False, "error": error_msg, "gmail_api_disabled": True}
                else:
                    logger.error(f"Gmail API error: {res.status_code} - {res.text}")
                    return {"success": False, "error": res.text}
        except Exception as e:
            logger.error(f"Exception during Gmail OAuth send: {e}")
            return {"success": False, "error": str(e)}

gmail_client = GmailClient()
