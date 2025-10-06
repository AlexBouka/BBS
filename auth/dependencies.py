from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User, UserRole
from core.db_handler import db_handler
from .jwt_utils import jwt_manager

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> User:
    """
    Fetch the currently authenticated user from the database.

    This function first verifies the JWT token provided in the Authorization header,
    and then uses the user ID extracted from the token to fetch the user from the database.
    If the token is invalid, or if the user is not found or is inactive,
    an HTTPException is raised with a 401 Unauthorized status code.

    :return: The currently authenticated user.
    :raises HTTPException: If the token is invalid, or if the user is not found or is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Verify token
        payload = jwt_manager.verify_token(token)
        if payload is None:
            raise credentials_exception

        # Extract user info from token
        user_id_str: str = payload.get("user_id")
        if user_id_str is None:
            raise credentials_exception

        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, AttributeError):
            raise credentials_exception

        # Check token type
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

    except Exception:
        raise credentials_exception

    # Fetch user from database
    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Fetch the currently authenticated user from the database, but only if the user is active.

    This function first fetches the currently authenticated user using the `get_current_user`
    dependency, and then checks if the user is active. If the user is inactive,
    an HTTPException is raised with a 400 Bad Request status code.

    :return: The currently authenticated user if the user is active.
    :raises HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Fetch the currently authenticated user from the database, but only if the user is an administrator.

    This function first fetches the currently authenticated user using the `get_current_user`
    dependency, and then checks if the user is an administrator. If the user is not an administrator,
    an HTTPException is raised with a 403 Forbidden status code.

    :return: The currently authenticated user if the user is an administrator.
    :raises HTTPException: If the user is not an administrator.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> Optional[User]:
    """
    Fetch the currently authenticated user from the database, but only if valid credentials are provided.

    If no credentials are provided, or if the credentials are invalid, None is returned.

    If the user is inactive, None is returned.

    :return: The currently authenticated user if valid credentials are provided and the user is active.
    :raises: No exceptions are raised by this function.
    """
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt_manager.verify_token(token)
        if payload is None:
            return None

        user_id: int = payload.get("user_id")
        if user_id is None:
            return None

        user = await session.get(User, user_id)
        if user and user.is_active:
            return user

    except Exception:
        pass

    return None
