from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.artwork import Artwork


class Artist(TimestampMixin, Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    profile_image_key: Mapped[str | None] = mapped_column(String(500))  # 저장소 키 (URL 아님)

    # 비동기 환경에서 의도치 않은 지연 로딩을 막기 위해 raise — 필요하면 쿼리에서 명시적으로 로딩
    artworks: Mapped[list["Artwork"]] = relationship(back_populates="artist", lazy="raise")
