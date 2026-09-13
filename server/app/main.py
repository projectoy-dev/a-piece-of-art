from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.cms.deps import CmsLoginRequired, redirect_to_login
from app.cms.router import cms_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import NotFoundError, not_found_handler
from app.core.logging import setup_logging

CMS_STATIC_DIR = Path(__file__).parent / "cms" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    await engine.dispose()


app = FastAPI(title="a-piece-of-art API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# CMS 로그인 세션 (서명된 쿠키)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.cms_session_secret,
    session_cookie="cms_session",
    path="/cms",
    same_site="lax",
    https_only=settings.app_env != "local",
)

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(CmsLoginRequired, redirect_to_login)

app.include_router(api_router, prefix="/api/v1")  # JSON API — front가 호출
app.include_router(cms_router, prefix="/cms")  # CMS HTML 화면 — 관리자가 접속
app.mount("/cms/static", StaticFiles(directory=CMS_STATIC_DIR), name="cms-static")

if settings.storage_backend == "local":
    # 로컬 전용: 업로드한 이미지를 /media 로 서빙 (운영은 CloudFront가 전송)
    Path(settings.media_root).mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.media_root), name="media")
