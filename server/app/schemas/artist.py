from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.utils.media import media_url


class ArtistSummary(BaseModel):
    """작품 응답 안에 포함되는 작가 요약"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ArtistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None
    profile_image_key: str | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def profile_image_url(self) -> str | None:
        return media_url(self.profile_image_key)
