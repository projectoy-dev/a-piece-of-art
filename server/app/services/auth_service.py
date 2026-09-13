from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """로그인 검증. 공개 API(JWT)와 CMS(세션)가 함께 사용합니다."""

    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.users.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_active_user(self, user_id: int) -> User | None:
        user = await self.users.get(user_id)
        if user is None or not user.is_active:
            return None
        return user
