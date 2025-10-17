import enum
import uuid

from sqlalchemy import Column, String, Integer, Boolean, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class BusType(enum.Enum):
    MINIBUS = "minibus"
    STANDARD = "stamdard"
    LUXURY = "luxury"
    SLEEPER = "sleeper"
    MINIBUS_LUXURY = "minibus_luxury"


class BusStatus(enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    DELETED = "deleted"


class Bus(Base):
    __tablename__ = "buses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Information
    bus_number = Column(String(50), unique=True, nullable=False, index=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    bus_name = Column(String(100), nullable=True)

    # Bus specifications
    bus_type = Column(Enum(BusType), nullable=False, default=BusType.STANDARD)
    capacity = Column(Integer, nullable=False)
    manufacturer = Column(String(50), nullable=True)
    model = Column(String(50), nullable=True)
    year_manufactured = Column(Integer, nullable=True)

    # Amenities (boolean flags)
    has_wifi = Column(Boolean, default=False)
    has_ac = Column(Boolean, default=False)
    has_tv = Column(Boolean, default=False)
    has_charging_ports = Column(Boolean, default=False)
    has_refreshments = Column(Boolean, default=False)
    has_restroom = Column(Boolean, default=False)

    # Operational status
    status = Column(Enum(BusStatus), nullable=False, default=BusStatus.ACTIVE)
    is_accessible = Column(Boolean, default=False)

    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Ownership/Management
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    operator_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    created_by = relationship(
        "User", foreign_keys=[created_by_id], backref="created_buses")
    operator = relationship(
        "User", foreign_keys=[operator_id], backref="operated_buses")

    def __repr__(self):
        return f"<Bus(bus_number='{self.bus_number}', type='{self.bus_type.value}', capacity={self.capacity})>"

    @property
    def is_operational(self) -> bool:
        return self.status == BusStatus.ACTIVE

    @property
    def amenities_list(self) -> list[str]:
        amenities = []
        if self.has_wifi:
            amenities.append("WiFi")
        if self.has_ac:
            amenities.append("AC")
        if self.has_tv:
            amenities.append("TV")
        if self.has_charging_ports:
            amenities.append("Charging Ports")
        if self.has_restroom:
            amenities.append("Restroom")
        if self.has_refreshments:
            amenities.append("Refreshments")
        if self.is_accessible:
            amenities.append("Wheelchair Accessible")
        return amenities
