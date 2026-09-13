from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "로그인 계정 (API 로그인 · CMS 관리자)"}

    id: Mapped[int] = mapped_column(primary_key=True, comment="사용자 ID")
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, comment="로그인 이메일 (고유)"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), comment="비밀번호 해시 (pwdlib 권장 알고리즘)"
    )
    name: Mapped[str] = mapped_column(String(100), default="", comment="표시 이름")
    is_active: Mapped[bool] = mapped_column(
        default=True, comment="로그인 허용 여부 — false면 로그인 · 토큰 인증 거부"
    )
    is_admin: Mapped[bool] = mapped_column(default=False, comment="CMS 접근 권한")
