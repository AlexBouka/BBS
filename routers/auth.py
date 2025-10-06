import logging
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError

from models import User, UserRole
from schemas.user import (
    UserCreate, UserResponse, UserDeleteResponse, UserLogin,
    PasswordConfirmationSchema)
from schemas.jwt import TokenResponse, TokenRefresh
from core.db_handler import db_handler
from auth.pass_utils import pwd_utils
from auth.jwt_utils import jwt_manager
from auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Setup templates
templates = Jinja2Templates(directory="frontend/templates")

# ===============================================================================
# PAGE ROUTES (Serve HTML)
# ===============================================================================


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "show_nav": True, "show_footer": True}
        )


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "show_nav": True, "show_footer": True}
        )


@router.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "show_nav": True, "show_footer": True}
        )


# ===============================================================================
# API ROUTES (Return JSON)
# ===============================================================================


# USER REGISTRATION, SOFT/HARD DELETION AND REACTIVATION ENDPOINTS (20-)
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and username validation"
    )
async def register_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(db_handler.session_dependency)
        ) -> UserResponse:
    """
    Register a new user.

    This endpoint creates a new user account with email and username validation.
     It will raise a 400 Bad Request error if the username or email already exists.
     It will raise a 500 Internal Server Error if there is an error creating the user.

    :param user_data: UserCreate instance containing the user's details.
    :param session: AsyncSession instance to interact with the database.
    :return: UserResponse instance containing the newly created user's details.
    """
    try:
        # Check if username already exists
        existing_username = await session.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists."
            )

        # Check if email already exists
        existing_email = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )

        # Hash the password
        hashed_password = pwd_utils.hash_password(user_data.password)

        # Create new user instance
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phoner_number,
            is_active=True,
            is_verified=False
        )

        # Save to Database
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Log successful registration
        logger.info(f"New user registered: {new_user.username} ({new_user.email})")

        # Return user data (password hash is excluded by UserResponse schema (schemas.user.UserResponse))
        return new_user

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists."
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occured during registration: {e}"
        )


@router.delete(
    "/users/me",
    response_model=UserDeleteResponse,
    summary="Delete current user account",
    description="Delete the account of the currently authenticated user (soft delete)"
    )
async def delete_current_user(
        password_confirmation: PasswordConfirmationSchema,
        session: AsyncSession = Depends(db_handler.session_dependency),
        current_user: User = Depends(get_current_user)
        ) -> UserDeleteResponse:
    """
    Delete the account of the currently authenticated user (soft delete).

    This endpoint is used to delete the account of the currently authenticated user.
    It is a soft delete, meaning that the user's data is not permanently deleted from the database,
    but instead marked as inactive.

    The endpoint requires the user to provide their password for confirmation.
    If the password is incorrect, a 400 Bad Request response is returned.
    If the deletion is successful, a 200 OK response is returned with the deleted user's ID and username.

    If an unexpected error occurs while deleting the user account, a 500 Internal Server Error response is returned.

    :param password_confirmation: The password to confirm the deletion of the user account.
    :param session: The database session to use.
    :param current_user: The currently authenticated user.
    :return: A UserDeleteResponse object containing the deleted user's ID and username.
    :raises HTTPException: If the password confirmation is invalid, or if an unexpected error occurs while deleting the user account.
    """
    try:
        # Verify if password is correct
        if not pwd_utils.verify_password(
                password_confirmation.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password confirmation"
            )

        # Soft delete: set is_active to False
        current_user.is_active = False
        current_user.email = f"deleted_{current_user.id}_{current_user.email}"
        current_user.username = f"deleted_{current_user.id}_{current_user.username}"

        await session.commit()

        logger.info(f"User account deleted (soft): {current_user.id} - {current_user.username}")

        return UserDeleteResponse(
            message="User account successfully deleted (soft delete)",
            deleted_user_id=current_user.id,
            username=current_user.username
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleteing user (id: {current_user.id} <{current_user.username}>): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while deleting the user account."
        )


@router.delete(
    "/admin/users/{user_id}",
    response_model=UserDeleteResponse,
    summary="Admin: Delete a user account",
    description="Admin endpoint to delete a user account by user ID (soft delete)"
)
async def admin_delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_current_user)
) -> UserDeleteResponse:
    """
    Admin endpoint to delete a user account by user ID (soft delete).

    This endpoint can only be accessed by administrators.

    The endpoint deletes the user account by setting the 'is_active' field to False,
    and anonymizing the user's username and email.

    If the user to be deleted is not found, a 404 Not Found response is returned.

    If the current user is not an administrator, a 403 Forbidden response is returned.

    If the current user is trying to delete themselves through this endpoint,
    a 400 Bad Request response is returned with a detail message indicating that
    the /users/me endpoint should be used instead.

    If an unexpected error occurs while deleting the user account,
    a 500 Internal Server Error response is returned.

    :param user_id: The ID of the user to be deleted.
    :param session: The database session to use.
    :param current_user: The currently authenticated user.
    :return: A UserDeleteResponse object containing the deleted user's ID and username.
    :raises HTTPException: If the user to be deleted is not found, or if the current user is not an administrator,
        or if an unexpected error occurs while deleting the user account.
    """
    try:
        # Check if current user is admin
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete user accounts"
            )

        # Fetch the user to be deleted
        target_user = await session.get(User, user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent admin from deleting themselves through this endpoint
        if target_user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use /users/me endpoint to delete your own account"
            )

        # Soft delete: set is_active to False and anonymize username/email
        original_username = target_user.username
        target_user.is_active = False
        target_user.email = f"deleted_{target_user.id}_{target_user.email}"
        target_user.username = f"deleted_{target_user.id}_{target_user.username}"

        await session.commit()

        logger.info(
            f"User (id: {target_user.id} <{original_username}>) \
            deleted by admin (id: {current_user.id} <{current_user.username}>)")

        return UserDeleteResponse(
            message=f"User account {original_username} successfully deleted by admin (soft delete)",
            deleted_user_id=target_user.id,
            username=target_user.username
        )

    except HTTPException:
        await session.rollback()
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Error in admin user deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while deleting the user account."
        )


@router.delete(
    "/admin/users/{user_id}/hard-delete",
    summary="Admin: Permanently delete a user account",
    description="Permanently remove user and all associated data - USE WITH CAUTION"
)
async def admin_hard_delete_user(
    user_id: UUID,
    password_confirmation: PasswordConfirmationSchema,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Admin endpoint to permanently delete a user account.

    This endpoint requires the admin to confirm their password to prevent accidental deletions.

    The endpoint will delete the user and all associated records, and cannot be undone.

    If the admin is not authenticated, a 403 Forbidden response is returned.

    If the admin's password confirmation is invalid, a 400 Bad Request response is returned.

    If the user to be deleted is not found, a 404 Not Found response is returned.

    If the admin is trying to delete themselves, a 400 Bad Request response is returned with a detail message indicating that
    the /users/me endpoint should be used instead.

    If an unexpected error occurs while deleting the user account,
    a 500 Internal Server Error response is returned.
    """
    try:
        # Verify admin credentials
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can perform hard deletions"
            )

        # Verify admin password
        if not pwd_utils.verify_password(
                password_confirmation.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin password confirmation"
            )

        # Fetch the user to be hard deleted
        target_user = await session.get(User, user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent admin from deleting themselves
        if target_user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Administrators cannot hard delete their own accounts"
            )

        deleted_username = target_user.username
        deleted_id = target_user.id

        # Hard delete (will cascade to related records)
        await session.delete(target_user)
        await session.commit()

        logger.critical(
            f"User (id: {deleted_id} <{deleted_username}>) \
            permanently deleted by admin (id: {current_user.id} <{current_user.username}>)"
        )

        return {
            "message": f"User account {deleted_username} permanently deleted by admin",
            "deleted_user_id": deleted_id,
            "deleted_username": deleted_username,
            "warning": "This action cannot be undone"
        }

    except HTTPException:
        await session.rollback()
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Error in admin hard user deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while permanently deleting the user account."
        )


@router.post(
    "/admin/users/{user_id}/reactivate",
    response_model=UserResponse,
    summary="Admin: Reactivate a soft-deleted user account",
    description="Admin endpoint to reactivate a soft-deleted user account by user ID"
)
async def admin_reactivate_user(
    user_id: UUID,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Admin endpoint to reactivate a soft-deleted user account by user ID.

    Only administrators can use this endpoint.

    If the user to be reactivated is not found, a 404 Not Found response is returned.

    If the user account is already active, a 400 Bad Request response is returned with a detail message indicating that the user account is already active.

    If an unexpected error occurs while reactivating the user account, a 500 Internal Server Error response is returned.

    :param user_id: The ID of the user to be reactivated.
    :return: The reactivated user's details.
    :raises HTTPException: If the user is not found, or if the user account is already active.
    """
    try:
        # Check admin permissions
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can reactivate user accounts"
            )

        # Fetch the user to be reactivated
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is already active"
            )

        # Reactivate the user
        user.is_active = True

        # Restore original username/email by removing "deleted_" prefix
        if user.username.startswith(f"deleted_{user.id}_"):
            user.username = user.username.replace(f"deleted_{user.id}_", "", 1)
        if user.email.startswith(f"deleted_{user.id}_"):
            user.email = user.email.replace(f"deleted_{user.id}_", "", 1)

        await session.commit()
        await session.refresh(user)

        logger.info(
            f"User account reactivated: {user.id} - {user.username} \
            by admin {current_user.id} - {current_user.username}")

        return user

    except HTTPException:
        await session.rollback()
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Error reactivating user (id: {user_id} <{user.username}>): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while reactivating the user account."
        )


# USER LOGIN/LOGOUT, CURRENT USER AND TOKEN MANAGEMENT ENDPOINTS
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login and token generation",
    description="Authenticate user and return JWT tokens"
)
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    This endpoint is used to authenticate a user and generate JWT tokens.
    The endpoint requires a username or email and a password to be provided.
    If the username/email or password is incorrect, a 401 Unauthorized response is returned.
    If the user account is inactive, a 401 Unauthorized response is returned with a detail message indicating that the user account is inactive.
    If an unexpected error occurs during login, a 500 Internal Server Error response is returned.

    :param login_data: UserLogin instance containing the user's credentials.
    :param session: The database session to use.
    :return: A TokenResponse object containing the generated JWT tokens.
    :raises HTTPException: If the username/email or password is incorrect, or if the user account is inactive, or if an unexpected error occurs during login.
    """
    try:
        # Find user by username or email
        print("Searching for:", login_data.username_or_email.lower())
        result = await session.execute(
            select(User).where(
                or_(
                    func.lower(User.username) == login_data.username_or_email.lower(),
                    func.lower(User.email) == login_data.username_or_email.lower()
                )
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password (user not found)",
            )

        # Verify password
        if not pwd_utils.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        # Create token payload
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        # Generate tokens
        access_token = jwt_manager.create_access_token(data=token_data)
        refresh_token = jwt_manager.create_refresh_token(data={"user_id": user.id})

        logger.info(f"User logged in: {user.id} - <{user.username}>")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 2
        )

    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured during login."
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using a valid refresh token"
)
async def refresh_token(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> TokenResponse:
    """
    Refreshes an access token using a valid refresh token.

    If the refresh token is invalid or has expired, a 401 Unauthorized response is returned.

    If the user associated with the refresh token is inactive, a 401 Unauthorized response is returned.

    If an unexpected error occurs while refreshing the token, a 500 Internal Server Error response is returned.

    :param token_data: The refresh token data.
    :return: A new access token and refresh token.
    :raises HTTPException: If the refresh token is invalid, expired, or if the associated user is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verify refresh token
        payload = jwt_manager.verify_token(token_data.refresh_token)
        if payload is None:
            raise credentials_exception

        # Check token type
        if payload.get("type") != "refresh":
            raise credentials_exception

        # Extract user
        user_id: int = payload.get("user_id")
        if not user_id:
            raise credentials_exception

        user = await session.get(User, user_id)
        if not user or not user.is_active:
            raise credentials_exception

        # Create new tokens
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        new_access_token = jwt_manager.create_access_token(data=token_data)
        new_refresh_token = jwt_manager.create_refresh_token(data={"user_id": user.id})

        logger.info(f"Token refreshed for user: {user.id} - <{user.username}>")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 2
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise credentials_exception


@router.post(
    "/logout",
    summary="Logout user (client-side token discard)",
    description="Client should discard tokens; server does not track token state"
)
async def logout_user(
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Client should discard tokens; server does not track token state.

    This endpoint is purely informative and does not perform any server-side action.
    It is intended to be used by clients to notify the server that a user has logged out,
    and that the associated token should be discarded.

    The server does not store any information about tokens, and does not revoke or blacklist
    tokens when a user logs out.

    The endpoint returns a message indicating that the user has been successfully logged out,
    as well as instructions to discard the token from client storage.

    :return: A dictionary containing a message and instructions.
    """
    logger.info(f"User logged out: {current_user.id} - <{current_user.username}>")
    return {
        "message": "Successfully logged out",
        "instructions": "Please remove the token from client storage"
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    description="Get information about the currently authenticated user"
)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Get information about the currently authenticated user.

    This endpoint returns information about the currently authenticated user.

    :return: A UserResponse object containing the user's information.
    :raises HTTPException: If the user is not authenticated.
    """
    return current_user
