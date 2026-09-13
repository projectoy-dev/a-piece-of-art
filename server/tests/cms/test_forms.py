import io

import pytest
from starlette.datastructures import UploadFile

from app.cms.forms import FormError, parse_image


def test_parse_image_without_file_returns_none():
    assert parse_image(None) is None
    assert parse_image(UploadFile(file=io.BytesIO(b""), filename="")) is None


def test_parse_image_rejects_unknown_extension():
    with pytest.raises(FormError):
        parse_image(UploadFile(file=io.BytesIO(b"x"), filename="virus.exe"))
