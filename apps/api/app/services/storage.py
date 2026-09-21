import boto3
from botocore.config import Config
from app.config import settings


class StorageService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None and settings.R2_ENDPOINT_URL and settings.R2_ACCESS_KEY_ID:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        return self._client

    def generate_presigned_upload_url(
        self,
        r2_key: str,
        content_type: str,
        expires_in: int = 300,
    ) -> str:
        """Genera una URL prefirmada HTTP PUT para carga directa a Cloudflare R2."""
        if not self.client:
            # Fallback simulado para entorno de desarrollo sin R2 configurado
            return f"https://mock-r2.local/{settings.R2_BUCKET_NAME}/{r2_key}?mock_token=presigned"

        return self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.R2_BUCKET_NAME,
                "Key": r2_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def generate_presigned_download_url(
        self,
        r2_key: str,
        expires_in: int = 3600,
    ) -> str:
        """Genera una URL prefirmada HTTP GET para descarga de archivos privados."""
        if not self.client:
            return f"https://mock-r2.local/{settings.R2_BUCKET_NAME}/{r2_key}?download=true"

        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.R2_BUCKET_NAME,
                "Key": r2_key,
            },
            ExpiresIn=expires_in,
        )

    def get_file_url(self, r2_key: str | None) -> str | None:
        """Obtiene la URL de acceso publico o prefirmada de un archivo."""
        if not r2_key:
            return None
        if settings.R2_PUBLIC_DOMAIN:
            return f"{settings.R2_PUBLIC_DOMAIN.rstrip('/')}/{r2_key}"
        return self.generate_presigned_download_url(r2_key)


storage_service = StorageService()
