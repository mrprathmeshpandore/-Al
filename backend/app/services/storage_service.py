import os
import logging
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseStorageService(ABC):
    @abstractmethod
    def save_file(self, file_data: bytes, stored_filename: str) -> str:
        """Save file bytes to storage and return storage reference/path."""
        pass

    @abstractmethod
    def get_file(self, stored_filename: str) -> bytes:
        """Retrieve file bytes from storage."""
        pass

    @abstractmethod
    def delete_file(self, stored_filename: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def file_exists(self, stored_filename: str) -> bool:
        """Check if file exists in storage."""
        pass


class LocalStorageService(BaseStorageService):
    """
    Local filesystem implementation of storage service.
    Default for local development and testing.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.STORAGE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, stored_filename: str) -> str:
        # Prevent directory traversal attacks
        safe_filename = os.path.basename(stored_filename)
        return os.path.join(self.base_dir, safe_filename)

    def save_file(self, file_data: bytes, stored_filename: str) -> str:
        file_path = self._get_path(stored_filename)
        with open(file_path, "wb") as f:
            f.write(file_data)
        logger.info(f"Saved file locally: {file_path}")
        return file_path

    def get_file(self, stored_filename: str) -> bytes:
        file_path = self._get_path(stored_filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found in local storage: {stored_filename}")
        with open(file_path, "rb") as f:
            return f.read()

    def delete_file(self, stored_filename: str) -> bool:
        file_path = self._get_path(stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted local file: {file_path}")
            return True
        return False

    def file_exists(self, stored_filename: str) -> bool:
        file_path = self._get_path(stored_filename)
        return os.path.exists(file_path)


class S3StorageService(BaseStorageService):
    """
    Amazon S3 / S3-compatible Object Storage implementation.
    Used for production cloud deployments.
    """

    def __init__(self):
        self.bucket = settings.STORAGE_BUCKET
        self.region = settings.STORAGE_REGION
        self.endpoint = settings.STORAGE_ENDPOINT or None
        self.access_key = settings.STORAGE_ACCESS_KEY
        self.secret_key = settings.STORAGE_SECRET_KEY
        self._s3_client = None

        try:
            import boto3
            session = boto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
            self._s3_client = session.client("s3", endpoint_url=self.endpoint)
            logger.info(f"S3 Storage service initialized for bucket '{self.bucket}'.")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 client: {e}. Falling back to local storage.")
            self._s3_client = None

    def save_file(self, file_data: bytes, stored_filename: str) -> str:
        if not self._s3_client or not self.bucket:
            return LocalStorageService().save_file(file_data, stored_filename)

        safe_filename = os.path.basename(stored_filename)
        try:
            self._s3_client.put_object(
                Bucket=self.bucket,
                Key=safe_filename,
                Body=file_data
            )
            logger.info(f"Uploaded file to S3: s3://{self.bucket}/{safe_filename}")
            return f"s3://{self.bucket}/{safe_filename}"
        except Exception as e:
            logger.error(f"S3 upload error for '{stored_filename}': {e}")
            raise e

    def get_file(self, stored_filename: str) -> bytes:
        if not self._s3_client or not self.bucket:
            return LocalStorageService().get_file(stored_filename)

        safe_filename = os.path.basename(stored_filename)
        try:
            response = self._s3_client.get_object(
                Bucket=self.bucket,
                Key=safe_filename
            )
            return response["Body"].read()
        except Exception as e:
            logger.error(f"S3 download error for '{stored_filename}': {e}")
            raise e

    def delete_file(self, stored_filename: str) -> bool:
        if not self._s3_client or not self.bucket:
            return LocalStorageService().delete_file(stored_filename)

        safe_filename = os.path.basename(stored_filename)
        try:
            self._s3_client.delete_object(
                Bucket=self.bucket,
                Key=safe_filename
            )
            logger.info(f"Deleted S3 object: s3://{self.bucket}/{safe_filename}")
            return True
        except Exception as e:
            logger.error(f"S3 delete error for '{stored_filename}': {e}")
            return False

    def file_exists(self, stored_filename: str) -> bool:
        if not self._s3_client or not self.bucket:
            return LocalStorageService().file_exists(stored_filename)

        safe_filename = os.path.basename(stored_filename)
        try:
            self._s3_client.head_object(Bucket=self.bucket, Key=safe_filename)
            return True
        except Exception:
            return False


_storage_instance: Optional[BaseStorageService] = None


def get_storage_service() -> BaseStorageService:
    """
    Singleton factory for storage service provider.
    Returns S3StorageService if STORAGE_PROVIDER == 's3', else LocalStorageService.
    """
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    provider = (settings.STORAGE_PROVIDER or "local").lower().strip()
    if provider in ("s3", "aws", "gcs") and settings.STORAGE_BUCKET:
        s3_service = S3StorageService()
        _storage_instance = s3_service
        return _storage_instance

    _storage_instance = LocalStorageService()
    return _storage_instance
