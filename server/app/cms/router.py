from fastapi import APIRouter

from app.cms.views import artworks, auth, dashboard

# CMS 화면은 OpenAPI 문서(front 타입 생성 대상)에서 제외
cms_router = APIRouter(include_in_schema=False)
cms_router.include_router(auth.router)
cms_router.include_router(dashboard.router)
cms_router.include_router(artworks.router)
