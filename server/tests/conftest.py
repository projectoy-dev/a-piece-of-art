import os

# 앱 import 전에 테스트용 환경변수 지정 (CI에서는 워크플로의 env가 우선)
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/app_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789")
os.environ.setdefault("CMS_SESSION_SECRET", "test-session-secret-0123456789abcdef012345")
os.environ.setdefault("STORAGE_BACKEND", "local")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
