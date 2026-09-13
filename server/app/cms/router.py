from fastapi import APIRouter

# CMS 화면은 OpenAPI 문서(front 타입 생성 대상)에서 제외
cms_router = APIRouter(include_in_schema=False)
