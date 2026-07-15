import chromadb
import logging
from src.app.config import settings

logger = logging.getLogger(__name__)

class VectorDBClient:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                # Try connecting to the HTTP service
                logger.info(f"Connecting to ChromaDB at {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}...")
                self._client = chromadb.HttpClient(
                    host=settings.CHROMADB_HOST,
                    port=int(settings.CHROMADB_PORT)
                )
                # Verify connection
                self._client.heartbeat()
                logger.info("ChromaDB connection successful.")
            except Exception as e:
                logger.warning(
                    f"Could not connect to ChromaDB at {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}. "
                    f"Falling back to EphemeralClient (in-memory). Error: {e}"
                )
                self._client = chromadb.EphemeralClient()
        return self._client

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
