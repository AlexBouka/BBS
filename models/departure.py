import uuid
import enum

from sqlalchemy import (
    Column, Enum, Text, Boolean, ForeignKey, DateTime
    )
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class DepartureStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    CANCELLED = "CANCELLED"
    DELAYED = "DELAYED"


class Departure(Base):
    __tablename__ = "departures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)

    bus_id = Column(
        UUID(as_uuid=True),
        ForeignKey("buses.id", ondelete="SET NULL"), nullable=True)

    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=True)

    status = Column(
        Enum(DepartureStatus),
        default=DepartureStatus.SCHEDULED, nullable=False)
    is_cancelled = Column(Boolean, default=False)
    is_full = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    route = relationship("Route", back_populates="departures")

    bus = relationship("Bus", back_populates="departures")

    @property
    def route_number(self):
        return self.route.route_number if self.route else None

    @property
    def bus_number(self):
        return self.bus.bus_number if self.bus else None

    @property
    def bus_type(self):
        return self.bus.bus_type if self.bus else None

    @property
    def capacity(self):
        return self.bus.capacity if self.bus else None

    @property
    def origin_city(self):
        return self.route.origin_city if self.route else None

    @property
    def destination_city(self):
        return self.route.destination_city if self.route else None

    @property
    def departure_date(self):
        """
        Returns the date of the departure time if set, else None.
        """
        return self.departure_time.date() if self.departure_time else None

    def __repr__(self):
        return (
            f"<Departure(route={self.route_id}, bus={self.bus_id}, "
            f"departure_time={self.departure_time})>"
        )
