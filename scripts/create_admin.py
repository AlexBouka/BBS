import asyncio
from uuid import uuid4
from sqlalchemy import select

from models import User, UserRole
from core.config import settings
from core.db_handler import db_handler
from auth.pass_utils import pwd_utils


async def create_admin_from_env() -> None:
    """Create an admin user from environment variables.

    This function creates an admin user from the environment variables
    `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`. If any of these
    variables are not set, the function will print a warning and return.

    If the admin user already exists, the function will print a message
    indicating that the user already exists.

    If the admin user does not already exist, the function will create the
    user with the specified credentials and mark them as verified.

    If an error occurs while creating the admin user, the function will
    print an error message.

    """
    username = settings.admin_username
    email = settings.admin_email
    password = settings.admin_password

    if not all([username, email, password]):
        print("Admin credentials not set in environment variables.")
        return

    async with db_handler.async_session_factory() as session:
        try:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Admin user {username} already exists.")
                return

            # Create admin
            admin = User(
                id=uuid4(),
                username=username,
                email=email,
                password_hash=pwd_utils.hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True  # Admin is pre-verified
            )

            session.add(admin)
            await session.commit()

            print(f"Admin user {username} created successfully.")

        except Exception as e:
            await session.rollback()
            print(f"Error creating admin user: {e}")


if __name__ == "__main__":
    asyncio.run(create_admin_from_env())
