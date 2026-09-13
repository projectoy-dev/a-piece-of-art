async def test_health(client):
    res = await client.get("/api/v1/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_openapi_contains_api_only(client):
    """front 타입 생성에 쓰는 OpenAPI에는 /api 경로만 있어야 합니다."""
    paths = (await client.get("/openapi.json")).json()["paths"]

    assert "/api/v1/artworks" in paths
    assert not any(path.startswith("/cms") for path in paths)
