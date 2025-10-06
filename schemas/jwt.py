from uuid import UUID
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Expiration time in seconds


class TokenRefresh(BaseModel):
    """
    Schema for token refresh request.
    """
    refresh_token: str


class TokenData(BaseModel):
    user_id: UUID
    username: str
    email: str
    role: str
