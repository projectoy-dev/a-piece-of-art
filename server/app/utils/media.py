from app.core.config import settings


def media_url(key: str | None) -> str | None:
    """저장소 키를 공개 URL로 변환합니다. 운영: https://img.example.com/{key}"""
    if not key:
        return None
    return f"{settings.media_base_url.rstrip('/')}/{key}"
