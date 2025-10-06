from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
import uuid


class Base(DeclarativeBase):
    # Common fields for all models
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
