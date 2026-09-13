from typing import Annotated

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import RedirectResponse

from app.api.deps import SessionDep
from app.cms.deps import SESSION_USER_KEY
from app.cms.templating import templates
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/login", name="cms_login")
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse(request, "auth/login.html", {"error": None, "email": ""})


@router.post("/login")
async def login(
    request: Request,
    session: SessionDep,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> Response:
    user = await AuthService(session).authenticate(email, password)
    if user is None or not user.is_admin:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "error": "이메일 또는 비밀번호가 올바르지 않거나 관리자 권한이 없습니다.",
                "email": email,
            },
            status_code=400,
        )
    request.session[SESSION_USER_KEY] = user.id
    return RedirectResponse(request.url_for("cms_dashboard"), status_code=303)


@router.post("/logout", name="cms_logout")
async def logout(request: Request) -> Response:
    request.session.clear()
    return RedirectResponse(request.url_for("cms_login"), status_code=303)
