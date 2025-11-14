from fastapi import HTTPException, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import User

exc_codes = {
    400: status.HTTP_400_BAD_REQUEST,
    401: status.HTTP_401_UNAUTHORIZED,
    403: status.HTTP_403_FORBIDDEN,
    404: status.HTTP_404_NOT_FOUND,
    409: status.HTTP_409_CONFLICT,
    500: status.HTTP_500_INTERNAL_SERVER_ERROR
}


def construct_http_exception(
        status_code: int, detail: str, headers: dict | None = None
        ) -> HTTPException:
    mapped_status_code = exc_codes.get(
        status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HTTPException(
        status_code=mapped_status_code, detail=detail, headers=headers
    )


async def get_user_by_username(
        username: str,
        session: AsyncSession
) -> User | None:
    """
    Fetch a user by their username.

    :param username: The username of the user to fetch.
    :param session: The database session to use.
    :return: The user if found, or None if not found.
    """
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    return user


async def get_user_by_email(
        email: str,
        session: AsyncSession
) -> User | None:
    """
    Fetch a user by their email.

    :param email: The email of the user to fetch.
    :param session: The database session to use.
    :return: The user if found, or None if not found.
    """
    result = await session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    return user


async def get_user_by_username_or_email(
        username_or_email: str,
        session: AsyncSession
) -> User | None:
    """
    Fetch a user by their username or email.

    :param username_or_email: The username or email of the user to fetch.
    :param session: The database session to use.
    :return: The user if found, or None if not found.
    """
    result = await session.execute(
        select(User).where(
            or_(
                func.lower(User.username) == username_or_email,
                func.lower(User.email) == username_or_email
            )
        )
    )
    user = result.scalar_one_or_none()
    return user


async def check_user_exists(
        username: str,
        email: str,
        session: AsyncSession
) -> bool:
    user_by_username = await get_user_by_username(username, session)
    if user_by_username:
        return True
    user_by_email = await get_user_by_email(email, session)

    return user_by_email is not None
