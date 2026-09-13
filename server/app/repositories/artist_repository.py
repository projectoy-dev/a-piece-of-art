from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artist


class ArtistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, artist_id: int) -> Artist | None:
        return await self.session.get(Artist, artist_id)

    async def list_all(self) -> list[Artist]:
        rows = await self.session.scalars(select(Artist).order_by(Artist.name))
        return list(rows)

    async def count(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(Artist)) or 0
