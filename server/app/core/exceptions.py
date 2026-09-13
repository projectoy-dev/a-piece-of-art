from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """서비스 계층에서 대상이 없을 때 발생. API에서는 404로 변환됩니다."""

    def __init__(self, resource: str, resource_id: int | str) -> None:
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} {resource_id} not found")


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
