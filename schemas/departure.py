import enum
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DepartureStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    CANCELLED = "CANCELLED"
    DELAYED = "DELAYED"


class DepartureBase(BaseModel):
    """
    Base Departure Schema.
    Includes common departure fields.
    """
    route_id: Optional[UUID] = None
    bus_id: Optional[UUID] = None
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    status: DepartureStatus = DepartureStatus.SCHEDULED
    is_cancelled: bool = False
    is_full: bool = False
    notes: Optional[str] = None
    bus: Optional[dict] = None

    @field_validator("departure_time")
    @classmethod
    def validate_departure_time(cls, value: datetime) -> datetime:
        now = datetime.now(timezone.utc)

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value <= now:
            raise ValueError("Departure time must be in the future")
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_arrival_time(cls, model):
        if model.arrival_time:
            if model.arrival_time.tzinfo is None:
                model.arrival_time = model.arrival_time.replace(
                    tzinfo=timezone.utc
                )
            if model.arrival_time <= model.departure_time:
                raise ValueError("Arrival time must be after departure time")
        return model


class DepartureCreate(DepartureBase):
    """
    Schema for departure creation.
    Inherits from DepartureBase.
    """
    pass


class DepartureUpdate(BaseModel):
    """
    Schema for departure updates.
    All fields are optional.
    """
    route_id: Optional[UUID] = None
    bus_id: Optional[UUID] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    status: Optional[DepartureStatus] = None
    is_cancelled: Optional[bool] = None
    is_full: Optional[bool] = None
    notes: Optional[str] = None


class DepartureResponse(DepartureBase):
    """
    Schema for departure responses.
    Includes id and computed fields.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    route_number: Optional[str] = None
    bus_number: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    available_seats: Optional[int] = None


class DepartureResponsePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    route_id: UUID
    bus_id: Optional[UUID] = None
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    status: DepartureStatus
    is_cancelled: bool
    is_full: bool

    bus_number: Optional[str] = None
    bus_type: Optional[str] = None
    capacity: Optional[int] = None
    has_wifi: Optional[bool] = None
    has_ac: Optional[bool] = None
    has_tv: Optional[bool] = None
    has_charging_ports: Optional[bool] = None
    has_refreshments: Optional[bool] = None
    is_accessible: Optional[bool] = None

    route_number: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None


class DepartureUpdateStatus(BaseModel):
    status: DepartureStatus = Field(
        ..., description="The new status for the departure")
    notes: Optional[str] = Field(None, description="Notes for the departure")


class RouteDepartureResponse(DepartureBase):
    pass


class DepartureListItem(BaseModel):
    """
    Departure List Item Schema
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    route_id: UUID
    bus_id: Optional[UUID] = None
    departure_time: datetime
    arrival_time: Optional[datetime] = None
    status: DepartureStatus
    is_cancelled: bool
    is_full: bool
    route_number: Optional[str] = None
    bus_number: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None


class DepartureSearchParams(BaseModel):
    """
    Departure Search Params Schema
    """
    route_id: Optional[UUID] = None
    bus_id: Optional[UUID] = None
    departure_date: Optional[datetime] = None
    status: Optional[DepartureStatus] = None
    is_cancelled: Optional[bool] = None
    is_full: Optional[bool] = None
