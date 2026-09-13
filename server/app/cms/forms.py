"""CMS 폼 데이터 → 스키마 변환 · 검증"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator
from starlette.datastructures import UploadFile

from app.schemas.artwork import ArtworkCreate, ArtworkUpdate
from app.services.storage_service import UploadedFile

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_IMAGE_BYTES = 20 * 1024 * 1024


class FormError(ValueError):
    pass


class ArtworkForm(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    year: int | None = Field(default=None, ge=0, le=9999)
    artist_id: int | None = None
    is_published: bool = False  # 체크박스: 체크 시 "on", 미체크 시 필드 없음

    @field_validator("description", "year", "artist_id", mode="before")
    @classmethod
    def empty_to_none(cls, value: Any) -> Any:
        return None if value == "" else value

    def to_create(self) -> ArtworkCreate:
        return ArtworkCreate(**self.model_dump())

    def to_update(self) -> ArtworkUpdate:
        return ArtworkUpdate(**self.model_dump())


def parse_image(value: Any) -> UploadedFile | None:
    """폼의 image 필드 검증. 파일을 선택하지 않았으면 None."""
    if not isinstance(value, UploadFile) or not value.filename:
        return None
    if Path(value.filename).suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise FormError("이미지는 jpg, png, webp, gif 파일만 올릴 수 있습니다.")
    if value.size is not None and value.size > MAX_IMAGE_BYTES:
        raise FormError("이미지는 20MB 이하만 올릴 수 있습니다.")
    return UploadedFile(file=value.file, filename=value.filename, content_type=value.content_type)


def error_messages(exc: ValidationError | FormError) -> list[str]:
    if isinstance(exc, FormError):
        return [str(exc)]
    return [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
