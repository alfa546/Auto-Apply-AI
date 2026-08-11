import imaplib
import email
import re
from email.header import decode_header
import logging
from typing import List
from sqlalchemy.orm import Session
from src.app.config import settings
from src.app.models import Application

logger = logging.getLogger(__name__)

class EmailInboxWatcher:
    """
    Watches the user's email inbox using IMAP.
    Identifies emails from companies where the user has active applications.
    """
    def __init__(self, user_email: str = None, user_password: str = None, access_token: str = None, use_oauth: bool = False):
        self.server = settings.EMAIL_IMAP_SERVER
        self.username = user_email or settings.EMAIL_ADDRESS
        self.password = user_password or settings.EMAIL_PASSWORD
        self.access_token = access_token
        self.use_oauth = use_oauth

    def _get_imap_connection(self) -> imaplib.IMAP4_SSL:
        if not self.server or not self.username:
            raise ValueError("IMAP email credentials are not fully configured in settings.")
        
        logger.info(f"Connecting to IMAP server: {self.server}")
        mail = imaplib.IMAP4_SSL(self.server)
        
        if self.use_oauth and self.access_token:
            auth_string = f"user={self.username}\x01auth=Bearer {self.access_token}\x01\x01"
            mail.authenticate('XOAUTH2', lambda x: auth_string.encode('utf-8'))
        else:
            if not self.password:
                raise ValueError("IMAP password is required for non-OAuth login.")
            mail.login(self.username, self.password)
            
        return mail

    def _decode_string(self, value) -> str:
        if not value:
            return ""
        decoded_parts = []
        for part_bytes, encoding in decode_header(value):
            if isinstance(part_bytes, bytes):
                decoded_parts.append(part_bytes.decode(encoding or "utf-8", errors="ignore"))
            else:
                decoded_parts.append(str(part_bytes))
        return "".join(decoded_parts)

    def _extract_email_body(self, msg) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except Exception:
                pass
        return body.strip()

    async def check_inbox(self, db: Session, user_id: str) -> List[dict]:
        """
        Connects to the inbox, fetches unread emails, filters by user's applied companies,
        and returns a list of matching email dictionaries.
        """
        # Fetch active applied companies for the user to filter spam
        applications = db.query(Application).filter(Application.user_id == user_id).all()
        if not applications:
            logger.info("No active applications found. Skipping email check.")
            return []

        company_names = {app.company.lower() for app in applications}
        logger.info(f"Scanning inbox for company responses from: {company_names}")

        matched_emails = []
        mail = None
        try:
            mail = self._get_imap_connection()
            mail.select("INBOX")

            # Search for unread/unseen emails
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                logger.warning("Failed to search inbox for unseen messages.")
                return []

            mail_ids = messages[0].split()
            logger.info(f"Found {len(mail_ids)} unseen emails in inbox.")

            for m_id in mail_ids:
                status, msg_data = mail.fetch(m_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_string(msg["Subject"])
                        sender = self._decode_string(msg["From"])
                        recipient = self._decode_string(msg["To"])
                        body = self._extract_email_body(msg)

                        # Extract the actual email address from "Name <addr>" headers
                        sender_addr = sender.lower()
                        addr_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", sender_addr)
                        if addr_match:
                            sender_addr = addr_match.group(0)
                        recipient_addr = recipient.lower()
                        addr_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", recipient_addr)
                        if addr_match:
                            recipient_addr = addr_match.group(0)

                        body_lower = body.lower()
                        subject_lower = subject.lower()

                        matched_app = None
                        matched_reason = None
                        for app in applications:
                            comp = app.company.lower()
                            company_domain_key = re.sub(r"[^a-zA-Z0-9]", "", comp)
                            if not company_domain_key:
                                continue
                            # Match company name in sender header, subject, body,
                            # or the company's domain inside the sender address.
                            if (
                                company_domain_key in sender_addr
                                or company_domain_key in recipient_addr
                                or comp in sender
                                or comp in subject_lower
                                or comp in body_lower
                            ):
                                matched_app = app
                                matched_reason = "company name/domain match"
                                break

                        if matched_app:
                            logger.info(f"Matched email from '{sender}' relating to application: {matched_app.company} ({matched_reason})")
                            matched_emails.append({
                                "sender": sender,
                                "recipient": recipient,
                                "subject": subject,
                                "body": body,
                                "application_id": matched_app.id,
                                "company": matched_app.company
                            })

        except Exception as e:
            logger.error(f"Error checking email inbox: {e}")
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass

        return matched_emails
