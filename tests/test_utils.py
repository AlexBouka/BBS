from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from models import User, UserRole
from auth.pass_utils import pwd_utils


async def create_test_admin_user(session: AsyncSession):
    username = settings.test_admin_username
    email = settings.test_admin_email
    password = settings.test_admin_password

    if not all([username, email, password]):
        print("Admin credentials not set in environment variables.")
        return

    try:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Admin user '{username}' already exists in test DB.")
            return

        admin = User(
            id=uuid4(),
            username=username,
            email=email,
            password_hash=pwd_utils.hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )

        session.add(admin)
        await session.commit()

    except Exception as e:
        print(f"Failed to create test admin user: {e}")
