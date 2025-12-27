"""MinIO service for object storage operations."""
import io
import json
from typing import Optional
from minio import Minio
from minio.error import S3Error
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MinIOService:
    """Service for interacting with MinIO object storage."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._ensure_buckets()

    def _ensure_buckets(self):
        """Ensure all required buckets exist."""
        buckets = [
            settings.bucket_raw_pdf,
            settings.bucket_parsed_json,
            settings.bucket_derived,
        ]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket}: {e}")
                raise

    def upload_pdf(self, doc_id: str, version_id: str, pdf_data: bytes) -> str:
        """
        Upload PDF to MinIO.

        Args:
            doc_id: Document ID
            version_id: Version ID
            pdf_data: PDF file bytes

        Returns:
            MinIO URI (bucket/path)
        """
        object_name = f"{doc_id}/{version_id}/source.pdf"
        try:
            self.client.put_object(
                settings.bucket_raw_pdf,
                object_name,
                io.BytesIO(pdf_data),
                length=len(pdf_data),
                content_type="application/pdf",
            )
            uri = f"{settings.bucket_raw_pdf}/{object_name}"
            logger.info(f"Uploaded PDF to {uri}")
            return uri
        except S3Error as e:
            logger.error(f"Error uploading PDF: {e}")
            raise

    def download_pdf(self, uri: str) -> bytes:
        """
        Download PDF from MinIO.

        Args:
            uri: MinIO URI (bucket/path)

        Returns:
            PDF bytes
        """
        bucket, object_name = uri.split("/", 1)
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading PDF from {uri}: {e}")
            raise

    def upload_json(self, doc_id: str, version_id: str, json_data: dict) -> str:
        """
        Upload normalized JSON result to MinIO.

        Args:
            doc_id: Document ID
            version_id: Version ID
            json_data: JSON data as dict

        Returns:
            MinIO URI (bucket/path)
        """
        object_name = f"{doc_id}/{version_id}/result.json"
        json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2).encode("utf-8")

        try:
            self.client.put_object(
                settings.bucket_parsed_json,
                object_name,
                io.BytesIO(json_bytes),
                length=len(json_bytes),
                content_type="application/json",
            )
            uri = f"{settings.bucket_parsed_json}/{object_name}"
            logger.info(f"Uploaded JSON to {uri}")
            return uri
        except S3Error as e:
            logger.error(f"Error uploading JSON: {e}")
            raise

    def download_json(self, uri: str) -> dict:
        """
        Download JSON from MinIO.

        Args:
            uri: MinIO URI (bucket/path)

        Returns:
            JSON data as dict
        """
        bucket, object_name = uri.split("/", 1)
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return json.loads(data.decode("utf-8"))
        except S3Error as e:
            logger.error(f"Error downloading JSON from {uri}: {e}")
            raise

    def upload_file(self, bucket: str, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload arbitrary file to MinIO.

        Args:
            bucket: Bucket name
            object_name: Object path
            data: File bytes
            content_type: MIME type

        Returns:
            MinIO URI (bucket/path)
        """
        try:
            self.client.put_object(
                bucket,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            uri = f"{bucket}/{object_name}"
            logger.info(f"Uploaded file to {uri}")
            return uri
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    def download_file(self, uri: str) -> bytes:
        """
        Download file from MinIO.

        Args:
            uri: MinIO URI (bucket/path)

        Returns:
            File bytes
        """
        bucket, object_name = uri.split("/", 1)
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file from {uri}: {e}")
            raise

    def delete_object(self, uri: str):
        """
        Delete object from MinIO.

        Args:
            uri: MinIO URI (bucket/path)
        """
        bucket, object_name = uri.split("/", 1)
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted object: {uri}")
        except S3Error as e:
            logger.error(f"Error deleting object {uri}: {e}")
            raise


# Global instance
minio_service = MinIOService()
