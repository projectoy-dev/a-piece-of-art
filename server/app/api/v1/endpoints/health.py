from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """ALB 대상 그룹 health check 경로"""
    return {"status": "ok"}
