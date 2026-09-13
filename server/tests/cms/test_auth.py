async def test_login_page_renders(client):
    res = await client.get("/cms/login")

    assert res.status_code == 200
    assert "로그인" in res.text


async def test_dashboard_redirects_to_login_without_session(client):
    res = await client.get("/cms/")

    assert res.status_code == 303
    assert res.headers["location"].endswith("/cms/login")
