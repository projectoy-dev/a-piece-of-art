from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.artist import Artist


class Artwork(TimestampMixin, Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None]
    image_key: Mapped[str | None] = mapped_column(String(500))  # 저장소 키 (URL 아님)
    is_published: Mapped[bool] = mapped_column(default=False, index=True)

    artist_id: Mapped[int | None] = mapped_column(
        ForeignKey("artists.id", ondelete="SET NULL"), index=True
    )
    artist: Mapped["Artist | None"] = relationship(back_populates="artworks", lazy="selectin")
