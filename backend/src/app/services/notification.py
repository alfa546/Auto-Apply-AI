import logging
import httpx
from typing import Optional
from src.app.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def send_discord_notification(message: str) -> bool:
        if not settings.DISCORD_WEBHOOK_URL:
            logger.info("Discord Webhook URL not configured. Skipping.")
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.DISCORD_WEBHOOK_URL,
                    json={"content": message},
                    timeout=5.0
                )
                if response.status_code in [200, 204]:
                    logger.info("Discord notification sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send Discord notification: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False

    @staticmethod
    async def send_telegram_notification(message: str) -> bool:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            logger.info("Telegram Bot Token or Chat ID not configured. Skipping.")
            return False
        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": settings.TELEGRAM_CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info("Telegram notification sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send Telegram notification: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False

    @classmethod
    async def send_notification(cls, message: str) -> dict:
        results = {}
        results["discord"] = await cls.send_discord_notification(message)
        results["telegram"] = await cls.send_telegram_notification(message)
        return results
