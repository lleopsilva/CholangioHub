from shared.config.settings import settings
from minio import Minio


def get_minio_client() -> Minio:
    # Use MinIO API port (9000) inside the Docker network regardless of host mapping
    endpoint = f"{getattr(settings, 'minio_host', 'minio')}:9000"
    return Minio(
        endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=False,
    )


def ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
