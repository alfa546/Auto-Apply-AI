from abc import ABC, abstractmethod
from typing import List, Dict

class BaseSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, country: str = "us") -> List[Dict]:
        """
        Search for opportunities using the provider.
        Returns a list of dictionaries with standard keys:
            title: str
            company: str
            location: str
            description: str
            url: str
            salary: str (optional)
            opportunity_type: str ('job', 'internship', 'scholarship', 'hackathon')
            raw_data: dict
        """
        pass
