from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artwork


class ArtworkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, artwork_id: int) -> Artwork | None:
        return await self.session.get(Artwork, artwork_id)

    async def list_page(
        self, *, offset: int, limit: int, published_only: bool
    ) -> tuple[list[Artwork], int]:
        stmt = select(Artwork)
        if published_only:
            stmt = stmt.where(Artwork.is_published.is_(True))

        total = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = await self.session.scalars(
            stmt.order_by(Artwork.id.desc()).offset(offset).limit(limit)
        )
        return list(rows), total or 0

    async def count(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(Artwork)) or 0

    async def add(self, artwork: Artwork) -> Artwork:
        self.session.add(artwork)
        await self.session.flush()
        return artwork

    async def delete(self, artwork: Artwork) -> None:
        await self.session.delete(artwork)
