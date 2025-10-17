from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime

from datetime import datetime


class Base(DeclarativeBase):
    # Common fields for all models
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
