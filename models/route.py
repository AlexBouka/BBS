import enum
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Enum, Text, JSON, ForeignKey
    )
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class RouteStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SEASONAL = "SEASONAL"
    DELETED = "DELETED"


class Route(Base):
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    route_number = Column(String(50), unique=True, nullable=False, index=True)
    route_name = Column(String(100), nullable=True)
    origin_city = Column(String(100), nullable=False, index=True)
    destination_city = Column(String(100), nullable=False, index=True)
    distance_km = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    intermediate_stops = Column(JSON, nullable=True)
    base_price = Column(Float, nullable=False)
    status = Column(
        Enum(RouteStatus), nullable=False, default=RouteStatus.ACTIVE)
    is_express = Column(Boolean, default=False)
    is_overnight = Column(Boolean, default=False)
    operates_daily = Column(Boolean, default=False)
    operating_days = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        )
    # created_by = relationship("User", backref="created_routes")
    created_by = relationship("User", back_populates="created_routes")

    departures = relationship(
        "Departure",
        back_populates="route",
        cascade="all, delete-orphan"
        )

    bus_routes = relationship(
        "BusRoute",
        back_populates="route",
        cascade="all, delete-orphan"
        )

    buses = relationship(
        "Bus",
        secondary="bus_routes",
        back_populates="routes",
        overlaps="bus_routes"
        )

    def __repr__(self):
        return (
            f"<Route(route_number='{self.route_number}', "
            f"{self.origin_city}→{self.destination_city})>"
        )

    @property
    def is_operational(self) -> bool:
        return self.status == RouteStatus.ACTIVE

    @property
    def estimated_duration_hours(self):
        return round(self.duration_minutes / 60, 2)

    @property
    def has_stops(self) -> bool:
        return self.intermediate_stops is not None and len(self.intermediate_stops) > 0

    @property
    def total_stops(self) -> int:
        if not self.intermediate_stops:
            return 0
        return len(self.intermediate_stops)

    def get_stop_cities(self):
        cities = [self.origin_city]
        if self.intermediate_stops:
            cities.extend(
                [stop.get("city") for stop in self.intermediate_stops])
        cities.append(self.destination_city)
        return cities
