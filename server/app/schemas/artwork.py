from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.artist import ArtistSummary
from app.utils.media import media_url


class ArtworkBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    year: int | None = Field(default=None, ge=0, le=9999)
    artist_id: int | None = None
    is_published: bool = False


class ArtworkCreate(ArtworkBase):
    pass


class ArtworkUpdate(BaseModel):
    """보낸 필드만 수정 (exclude_unset)"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    year: int | None = Field(default=None, ge=0, le=9999)
    artist_id: int | None = None
    is_published: bool | None = None


class ArtworkRead(ArtworkBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    artist: ArtistSummary | None = None
    image_key: str | None = Field(default=None, exclude=True)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def image_url(self) -> str | None:
        return media_url(self.image_key)
