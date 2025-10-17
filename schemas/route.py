import enum
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, field_validator, ConfigDict


class RouteStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SEASONAL = "SEASONAL"
    DELETED = "DELETED"


class IntermediateStopSchema(BaseModel):
    """
    Intermediate Stop Schema
    """
    city: str
    stop_duration_minutes: int
    distance_from_origin_km: int

    @field_validator("stop_duration_minutes")
    @classmethod
    def validate_stop_duration(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Stop duration must be non-negative")
        if value > 120:
            raise ValueError("Stop duration must be less than 120 minutes")
        return value

    @field_validator("distance_from_origin_km")
    @classmethod
    def validate_distance_from_origin(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Distance from origin must be positive")
        return value


class RouteBase(BaseModel):
    """
    Base Route Schema
    """
    route_number: str
    route_name: Optional[str] = None
    origin_city: str
    destination_city: str
    distance_km: int
    duration_minutes: int
    intermediate_stops: Optional[List[IntermediateStopSchema]] = None
    base_price: float
    is_express: bool = False
    is_overnight: bool = False
    operates_daily: bool = False
    operating_days: Optional[List[str]] = None
    description: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("route_number")
    @classmethod
    def validate_route_number(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Route number cannot be empty")
        return value.strip().upper()

    @field_validator("origin_city", "destination_city")
    @classmethod
    def validate_origin_and_destination_cities(clas, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Origin or destination city cannot be empty")
        return value.strip().title()

    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Distance must be positive")
        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value

    @field_validator("base_price")
    @classmethod
    def validate_base_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Base price must be positive")
        return value


class RouteCreate(RouteBase):
    """
    Route Create Schema
    """
    status: RouteStatus = RouteStatus.ACTIVE


class RouteUpdate(BaseModel):
    """
    Route Update Schema
    """
    route_number: Optional[str]
    route_name: Optional[str]
    origin_city: Optional[str]
    destination_city: Optional[str]
    distance_km: Optional[int]
    duration_minutes: Optional[int]
    intermediate_stops: Optional[List[IntermediateStopSchema]]
    base_price: Optional[float]
    is_express: Optional[bool]
    is_overnight: Optional[bool]
    operates_daily: Optional[bool]
    operating_days: Optional[List[str]]
    description: Optional[str]
    notes: Optional[str]


class RouteResponse(RouteBase):
    """
    Route Response Schema
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: RouteStatus
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    is_operational: bool
    estimated_duration_hours: float
    has_stops: bool
    total_stops: int


class RouteListItem(BaseModel):
    """
    Route List Item Schema
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    route_number: str
    route_name: Optional[str]
    origin_city: str
    destination_city: str
    distance_km: int
    estimated_duration_hours: float
    base_price: float
    status: RouteStatus
    is_express: bool
    is_operational: bool


class RouteSearchParams(BaseModel):
    """
    Route Search Params Schema
    """
    origin_city: Optional[str]
    destination_city: Optional[str]
    min_price: Optional[float]
    max_price: Optional[float]
    status: Optional[RouteStatus]
    is_express: Optional[bool]
