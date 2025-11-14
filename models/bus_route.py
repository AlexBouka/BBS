import uuid
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime


class BusRoute(Base):
    __tablename__ = "bus_routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bus_id = Column(
        UUID(as_uuid=True), ForeignKey("buses.id", ondelete="CASCADE"),
        nullable=False
        )
    route_id = Column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False
        )
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    bus = relationship(
        "Bus",
        back_populates="bus_routes",
        overlaps="buses,routes"
        )

    route = relationship(
        "Route",
        back_populates="bus_routes",
        overlaps="buses,routes"
        )

    def __repr__(self):
        return f"<BusRoute(bus_id={self.bus_id}, route_id={self.route_id})>"
