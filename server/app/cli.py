"""관리 명령.

사용법: uv run python -m app.cli create-admin --email admin@example.com --password ****
"""

import argparse
import asyncio

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import User
from app.repositories.user_repository import UserRepository


async def create_admin(email: str, password: str, name: str) -> None:
    async with SessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_by_email(email)
        if user:
            user.is_admin = True
            user.hashed_password = hash_password(password)
            print(f"기존 사용자 {email} 을(를) 관리자로 갱신했습니다.")
        else:
            await repo.add(
                User(email=email, hashed_password=hash_password(password), name=name, is_admin=True)
            )
            print(f"관리자 {email} 을(를) 만들었습니다.")
        await session.commit()
    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(prog="app.cli")
    commands = parser.add_subparsers(dest="command", required=True)

    admin = commands.add_parser("create-admin", help="CMS 관리자 계정 생성 (이미 있으면 갱신)")
    admin.add_argument("--email", required=True)
    admin.add_argument("--password", required=True)
    admin.add_argument("--name", default="관리자")

    args = parser.parse_args()
    if args.command == "create-admin":
        asyncio.run(create_admin(args.email, args.password, args.name))


if __name__ == "__main__":
    main()
