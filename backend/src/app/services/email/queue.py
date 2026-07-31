"""
Email sending queue with rate limiting.
Gmail limits: 500 emails/day, ~100 emails/hour for Google Workspace accounts.
"""

import time
import logging
from datetime import datetime, date
from collections import deque
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmailRateLimiter:
    def __init__(self, daily_limit: int = 450, hourly_limit: int = 90):
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
        self.sent_timestamps = deque()
    
    def can_send(self) -> bool:
        now = time.time()
        # Remove timestamps older than 24 hours
        while self.sent_timestamps and (now - self.sent_timestamps[0]) > 86400:
            self.sent_timestamps.popleft()
        
        # Check daily limit
        if len(self.sent_timestamps) >= self.daily_limit:
            return False
        
        # Check hourly limit
        hourly_count = sum(1 for t in self.sent_timestamps if (now - t) < 3600)
        if hourly_count >= self.hourly_limit:
            return False
        
        return True
    
    def record_send(self):
        self.sent_timestamps.append(time.time())
    
    def get_remaining_today(self) -> int:
        now = time.time()
        while self.sent_timestamps and (now - self.sent_timestamps[0]) > 86400:
            self.sent_timestamps.popleft()
        return self.daily_limit - len(self.sent_timestamps)

email_rate_limiter = EmailRateLimiter()
