import io

import pytest
from starlette.datastructures import UploadFile

from app.cms.forms import ArtworkForm, FormError, parse_image


def test_artwork_form_converts_empty_values():
    form = ArtworkForm.model_validate(
        {"title": "무제", "description": "", "year": "", "artist_id": "", "is_published": "on"}
    )

    assert form.description is None
    assert form.year is None
    assert form.artist_id is None
    assert form.is_published is True


def test_artwork_form_unchecked_checkbox_is_false():
    assert ArtworkForm.model_validate({"title": "무제"}).is_published is False


def test_parse_image_without_file_returns_none():
    assert parse_image(None) is None
    assert parse_image(UploadFile(file=io.BytesIO(b""), filename="")) is None


def test_parse_image_rejects_unknown_extension():
    with pytest.raises(FormError):
        parse_image(UploadFile(file=io.BytesIO(b"x"), filename="virus.exe"))
