import io

from app.core.config import settings
from app.services.storage_service import StorageService, UploadedFile


async def test_local_upload_and_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_backend", "local")
    monkeypatch.setattr(settings, "media_root", str(tmp_path))
    storage = StorageService()

    key = await storage.upload(
        UploadedFile(io.BytesIO(b"image-bytes"), "Photo.JPG", "image/jpeg"),
        prefix="uploads/1",
    )

    assert key.startswith("uploads/1/")
    assert key.endswith(".jpg")
    assert (tmp_path / key).read_bytes() == b"image-bytes"
    assert storage.url(key) == f"{settings.media_base_url}/{key}"

    await storage.delete(key)
    assert not (tmp_path / key).exists()
