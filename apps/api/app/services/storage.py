import boto3
from botocore.config import Config
from app.config import settings

SAMPLE_MEDIA_MAP = {
    "ceremonia.jpg": {
        "url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1519741497674-611481863552?w=400&auto=format&fit=crop&q=80",
    },
    "novios_brindis.jpg": {
        "url": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=400&auto=format&fit=crop&q=80",
    },
    "baile.jpg": {
        "url": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=400&auto=format&fit=crop&q=80",
    },
    "recepcion.jpg": {
        "url": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?w=400&auto=format&fit=crop&q=80",
    },
    "anillos.jpg": {
        "url": "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=400&auto=format&fit=crop&q=80",
    },
    "pastel.jpg": {
        "url": "https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=1600&auto=format&fit=crop&q=85",
        "thumb": "https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=400&auto=format&fit=crop&q=80",
    },
}


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
            # En desarrollo local sin R2, delegar al endpoint mock de subida directa
            return f"http://localhost:8000/api/a/upload-mock?key={r2_key}"

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
            for name, urls in SAMPLE_MEDIA_MAP.items():
                if name in r2_key:
                    return urls["thumb"] if "/thumbs/" in r2_key else urls["url"]
            return f"http://localhost:8000/media/{r2_key}?download=true"

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

        if r2_key.startswith("http://") or r2_key.startswith("https://"):
            return r2_key

        if settings.R2_PUBLIC_DOMAIN:
            return f"{settings.R2_PUBLIC_DOMAIN.rstrip('/')}/{r2_key}"

        if not self.client:
            for name, urls in SAMPLE_MEDIA_MAP.items():
                if name in r2_key:
                    return urls["thumb"] if "/thumbs/" in r2_key else urls["url"]
            return f"http://localhost:8000/media/{r2_key}"

        return self.generate_presigned_download_url(r2_key)


storage_service = StorageService()
