import enum
import uuid

from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class UserRole(enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # User role
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)

    # Additional user information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # created_at and updated_at fields are inherited from the Base class

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

    @property
    def full_name(self) -> str:
        """
        Returns the user's full name if it is available, otherwise returns the username.

        :return: The user's full name or username if full name is not available.
        :rtype: str
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_customer(self) -> bool:
        return self.role == UserRole.CUSTOMER

    @property
    def is_staff(self) -> bool:
        return self.role == UserRole.STAFF
