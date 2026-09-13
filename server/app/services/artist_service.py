from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Artist
from app.repositories.artist_repository import ArtistRepository


class ArtistService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ArtistRepository(session)

    async def list_artists(self) -> list[Artist]:
        return await self.repo.list_all()

    async def get_artist(self, artist_id: int) -> Artist:
        artist = await self.repo.get(artist_id)
        if artist is None:
            raise NotFoundError("Artist", artist_id)
        return artist

    async def count_artists(self) -> int:
        return await self.repo.count()
