import os
import uuid
import logging
from abc import ABC, abstractmethod
from firebase_admin import storage
from src.app.config import settings

logger = logging.getLogger(__name__)

class StorageProvider(ABC):
    @abstractmethod
    def upload(self, file_content: bytes, filename: str) -> str:
        """
        Uploads a file and returns its accessible URL.
        """
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload(self, file_content: bytes, filename: str) -> str:
        # Generate a unique name to prevent collisions
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(self.upload_dir, unique_filename)
        
        with open(filepath, "wb") as f:
            f.write(file_content)
        
        # Return path relative to server root or an absolute system path
        logger.info(f"File uploaded locally to {filepath}")
        return f"/uploads/{unique_filename}"


class FirebaseStorageProvider(StorageProvider):
    def upload(self, file_content: bytes, filename: str) -> str:
        try:
            bucket = storage.bucket()
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"resumes/{uuid.uuid4()}{file_ext}"
            blob = bucket.blob(unique_filename)
            blob.upload_from_string(file_content, content_type="application/pdf")
            
            # Make the blob publicly viewable or generate signed URL
            blob.make_public()
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload to Firebase storage: {e}. Falling back to local upload.")
            return LocalStorageProvider().upload(file_content, filename)


# Determine provider based on configuration
def get_storage_provider() -> StorageProvider:
    if settings.FIREBASE_STORAGE_BUCKET and settings.FIREBASE_PROJECT_ID != "your-firebase-project-id":
        return FirebaseStorageProvider()
    return LocalStorageProvider()

storage_service = get_storage_provider()
