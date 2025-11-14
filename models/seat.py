import uuid

from sqlalchemy import (
    Column, String, Boolean, ForeignKey
    )
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bus_id = Column(
        UUID(as_uuid=True),
        ForeignKey("buses.id", ondelete="CASCADE"), nullable=False)

    seat_number = Column(String(10), nullable=False)
    is_reserved = Column(Boolean, default=False)
    is_window_seat = Column(Boolean, default=False)

    bus = relationship("Bus", back_populates="seats")
