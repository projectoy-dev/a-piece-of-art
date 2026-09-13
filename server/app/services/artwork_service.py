from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Artwork
from app.repositories.artwork_repository import ArtworkRepository
from app.schemas.artwork import ArtworkCreate, ArtworkRead, ArtworkUpdate
from app.schemas.common import Page
from app.services.storage_service import StorageService, UploadedFile


class ArtworkService:
    """작품 비즈니스 로직. 공개 API와 CMS가 함께 사용합니다."""

    def __init__(self, session: AsyncSession, storage: StorageService | None = None) -> None:
        self.session = session
        self.repo = ArtworkRepository(session)
        self.storage = storage or StorageService()

    async def list_artworks(
        self, *, page: int, size: int, published_only: bool = True
    ) -> Page[ArtworkRead]:
        items, total = await self.repo.list_page(
            offset=(page - 1) * size, limit=size, published_only=published_only
        )
        return Page[ArtworkRead](
            items=[ArtworkRead.model_validate(a) for a in items], total=total, page=page, size=size
        )

    async def get_artwork(self, artwork_id: int, *, published_only: bool = True) -> Artwork:
        artwork = await self.repo.get(artwork_id)
        if artwork is None or (published_only and not artwork.is_published):
            raise NotFoundError("Artwork", artwork_id)
        return artwork

    async def count_artworks(self) -> int:
        return await self.repo.count()

    async def create_artwork(
        self, data: ArtworkCreate, image: UploadedFile | None = None
    ) -> Artwork:
        artwork = await self.repo.add(Artwork(**data.model_dump()))  # flush로 id 확보
        if image:
            artwork.image_key = await self.storage.upload(image, prefix=f"artworks/{artwork.id}")
        await self.session.commit()
        await self.session.refresh(artwork, ["artist"])
        return artwork

    async def update_artwork(
        self, artwork_id: int, data: ArtworkUpdate, image: UploadedFile | None = None
    ) -> Artwork:
        artwork = await self.get_artwork(artwork_id, published_only=False)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(artwork, field, value)

        old_key = None
        if image:
            old_key = artwork.image_key
            artwork.image_key = await self.storage.upload(image, prefix=f"artworks/{artwork.id}")

        await self.session.commit()
        await self.session.refresh(artwork, ["artist"])
        await self.storage.delete(old_key)  # DB 반영이 끝난 뒤 이전 이미지 삭제
        return artwork

    async def delete_artwork(self, artwork_id: int) -> None:
        artwork = await self.get_artwork(artwork_id, published_only=False)
        image_key = artwork.image_key
        await self.repo.delete(artwork)
        await self.session.commit()
        await self.storage.delete(image_key)
