from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse

from app.api.deps import SessionDep
from app.models import User
from app.services.auth_service import AuthService

SESSION_USER_KEY = "admin_user_id"


class CmsLoginRequired(Exception):
    """CMS 로그인이 필요할 때 발생 → 로그인 페이지로 리다이렉트"""


async def redirect_to_login(request: Request, exc: CmsLoginRequired) -> RedirectResponse:
    return RedirectResponse(request.url_for("cms_login"), status_code=303)


async def get_admin_user(request: Request, session: SessionDep) -> User:
    user_id = request.session.get(SESSION_USER_KEY)
    if user_id is None:
        raise CmsLoginRequired

    user = await AuthService(session).get_active_user(user_id)
    if user is None or not user.is_admin:
        request.session.clear()
        raise CmsLoginRequired
    return user


AdminUser = Annotated[User, Depends(get_admin_user)]
