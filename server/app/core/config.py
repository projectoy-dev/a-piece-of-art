from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱 설정. 로컬은 .env 파일, 운영은 ECS가 Parameter Store 값을 환경변수로 주입합니다."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"

    database_url: str
    secret_key: str
    cms_session_secret: str
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = ["http://localhost:3000"]

    storage_backend: Literal["local", "s3"] = "local"
    s3_bucket: str = ""
    media_base_url: str = "http://localhost:8000/media"
    media_root: str = "media"  # storage_backend=local 일 때 저장 위치


settings = Settings()
