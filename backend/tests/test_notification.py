import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from src.app.services.notification import NotificationService
from src.app.config import settings

class TestNotificationService(unittest.IsolatedAsyncioTestCase):
    @patch("src.app.config.settings.DISCORD_WEBHOOK_URL", None)
    async def test_discord_not_configured(self):
        res = await NotificationService.send_discord_notification("test message")
        self.assertFalse(res)

    @patch("src.app.config.settings.DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test")
    @patch("httpx.AsyncClient.post")
    async def test_discord_configured_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        res = await NotificationService.send_discord_notification("test message")
        self.assertTrue(res)
        mock_post.assert_called_once_with(
            "https://discord.com/api/webhooks/test",
            json={"content": "test message"},
            timeout=5.0
        )

    @patch("src.app.config.settings.TELEGRAM_BOT_TOKEN", None)
    @patch("src.app.config.settings.TELEGRAM_CHAT_ID", None)
    async def test_telegram_not_configured(self):
        res = await NotificationService.send_telegram_notification("test message")
        self.assertFalse(res)

    @patch("src.app.config.settings.TELEGRAM_BOT_TOKEN", "123456:ABC-DEF")
    @patch("src.app.config.settings.TELEGRAM_CHAT_ID", "987654321")
    @patch("httpx.AsyncClient.post")
    async def test_telegram_configured_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        res = await NotificationService.send_telegram_notification("test message")
        self.assertTrue(res)
        mock_post.assert_called_once_with(
            "https://api.telegram.org/bot123456:ABC-DEF/sendMessage",
            json={
                "chat_id": "987654321",
                "text": "test message",
                "parse_mode": "HTML"
            },
            timeout=5.0
        )

if __name__ == "__main__":
    unittest.main()
