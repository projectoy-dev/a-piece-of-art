from pydantic import BaseModel


class Page[T](BaseModel):
    """페이지네이션 응답"""

    items: list[T]
    total: int
    page: int
    size: int


class ErrorResponse(BaseModel):
    detail: str
