from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.schemas.artwork import ArtworkRead
from app.schemas.common import Page
from app.services.artwork_service import ArtworkService

router = APIRouter(prefix="/artworks", tags=["artworks"])


@router.get("")
async def list_artworks(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Page[ArtworkRead]:
    """공개된 작품 목록"""
    return await ArtworkService(session).list_artworks(page=page, size=size)


@router.get("/{artwork_id}")
async def get_artwork(artwork_id: int, session: SessionDep) -> ArtworkRead:
    artwork = await ArtworkService(session).get_artwork(artwork_id)
    return ArtworkRead.model_validate(artwork)
