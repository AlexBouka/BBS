import enum
import re
from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    STAFF = "STAFF"


class UserBase(BaseModel):
    """
    Base User Schema.
    Inherits from Pydantic BaseModel and includes common user fields.
    """
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if len(value) < 5:
            raise ValueError("Username must be at least 5 characters long.")
        if not re.match("^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username can only contain letters, numbers, and underscores.")
        return value.lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise ValueError("Invalid phone number format.")
        return value


class AdminCreate(UserBase):
    """
    Schema for admin creation.
    """
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 12:
            raise ValueError('Password must be at least 12 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character')
        return value


class UserCreate(UserBase):
    """
    User Creation Schema.
    Inherits from UserBase (same module) and adds password and role fields.
    """
    password: str
    role: UserRole = UserRole.CUSTOMER

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        return value


class UserUpdate(UserBase):
    """
    User Update Schema.
    Inherits from UserBase (same module) and adds optional fields.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) < 5:
            raise ValueError("Username must be at least 5 characters long.")
        if value and not re.match("^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username can only contain letters, numbers, and underscores.")
        return value.lower() if value else value


class UserResponse(UserBase):
    """
    User Response Schema.
    Inherits from UserBase (same module) and adds additional fields for responses.
    Excludes password for security reasons.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    full_name: str


class UserLogin(BaseModel):
    username_or_email: str
    password: str

    @field_validator("username_or_email")
    @classmethod
    def validate_username_or_email(cls, value: str) -> str:
        return value.lower()


class PasswordChangeSchema(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        return value


class UserDeleteResponse(BaseModel):
    """
    Response for user deletion.
    """
    message: str
    deleted_user_id: int
    username: str


class PasswordConfirmationSchema(BaseModel):
    """
    Schema for password confirmation during sensitive operations
    """
    password: str
