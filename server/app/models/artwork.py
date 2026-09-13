from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.artist import Artist


class Artwork(TimestampMixin, Base):
    __tablename__ = "artworks"
    __table_args__ = {"comment": "작품"}

    id: Mapped[int] = mapped_column(primary_key=True, comment="작품 ID")
    title: Mapped[str] = mapped_column(String(200), comment="작품 제목")
    description: Mapped[str | None] = mapped_column(Text, comment="작품 설명")
    year: Mapped[int | None] = mapped_column(comment="제작 연도")
    image_key: Mapped[str | None] = mapped_column(
        String(500), comment="작품 이미지 저장소 키 (URL 아님 — media_url()로 변환)"
    )
    is_published: Mapped[bool] = mapped_column(
        default=False, index=True, comment="공개 여부 — true인 작품만 사용자 API에 노출"
    )

    artist_id: Mapped[int | None] = mapped_column(
        ForeignKey("artists.id", ondelete="SET NULL"),
        index=True,
        comment="작가 ID — 작가 삭제 시 NULL",
    )
    artist: Mapped["Artist | None"] = relationship(back_populates="artworks", lazy="selectin")
