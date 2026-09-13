from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.artist import ArtistRead
from app.services.artist_service import ArtistService

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("")
async def list_artists(session: SessionDep) -> list[ArtistRead]:
    artists = await ArtistService(session).list_artists()
    return [ArtistRead.model_validate(a) for a in artists]


@router.get("/{artist_id}")
async def get_artist(artist_id: int, session: SessionDep) -> ArtistRead:
    artist = await ArtistService(session).get_artist(artist_id)
    return ArtistRead.model_validate(artist)
