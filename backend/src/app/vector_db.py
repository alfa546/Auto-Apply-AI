import chromadb
from src.app.config import settings

class VectorDBClient:
    def __init__(self):
        # Initialize HTTP client to connect to the docker service
        self.client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=int(settings.CHROMADB_PORT)
        )

    def get_or_create_collection(self, name: str):
        """
        Get an existing collection or create a new one with the given name.
        """
        return self.client.get_or_create_collection(name=name)

    def heartbeat(self) -> int:
        """
        Check database connectivity. Returns time in nanoseconds since epoch.
        """
        return self.client.heartbeat()

# Global client instance
vector_db = VectorDBClient()
