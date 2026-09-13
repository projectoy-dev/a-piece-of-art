import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.utils.media import media_url

# 키가 UUID라 같은 키에 덮어쓰지 않으므로 CloudFront에서 영구 캐시해도 안전
CACHE_CONTROL = "public, max-age=31536000, immutable"


@dataclass
class UploadedFile:
    file: BinaryIO
    filename: str
    content_type: str | None = None


class StorageService:
    """이미지 저장소. 로컬은 server/media/, 운영은 S3 (방문자에게는 CloudFront로 전송)."""

    def __init__(self) -> None:
        self.backend = settings.storage_backend
        self._s3 = None

    @property
    def s3(self):
        if self._s3 is None:
            import boto3  # 로컬 모드에서는 불필요하므로 지연 import

            self._s3 = boto3.client("s3")
        return self._s3

    async def upload(self, upload: UploadedFile, prefix: str) -> str:
        """파일을 저장하고 저장소 키를 반환합니다. DB에는 이 키만 저장합니다."""
        key = f"{prefix}/{uuid4()}{Path(upload.filename).suffix.lower()}"
        if self.backend == "s3":
            # boto3는 동기 라이브러리라 스레드풀에서 실행
            await run_in_threadpool(
                self.s3.upload_fileobj,
                upload.file,
                settings.s3_bucket,
                key,
                ExtraArgs={
                    "ContentType": upload.content_type or "application/octet-stream",
                    "CacheControl": CACHE_CONTROL,
                },
            )
        else:
            await run_in_threadpool(self._save_local, upload.file, key)
        return key

    async def delete(self, key: str | None) -> None:
        if not key:
            return
        if self.backend == "s3":
            await run_in_threadpool(self.s3.delete_object, Bucket=settings.s3_bucket, Key=key)
        else:
            (Path(settings.media_root) / key).unlink(missing_ok=True)

    def url(self, key: str | None) -> str | None:
        return media_url(key)

    @staticmethod
    def _save_local(fileobj: BinaryIO, key: str) -> None:
        path = Path(settings.media_root) / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            shutil.copyfileobj(fileobj, f)
