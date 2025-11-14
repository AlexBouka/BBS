import enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class BusType(str, enum.Enum):
    MINIBUS = "MINIBUS"
    STANDARD = "STANDARD"
    LUXURY = "LUXURY"
    SLEEPER = "SLEEPER"
    MINIBUS_LUXURY = "MINIBUS_LUXURY"


class BusStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class BusRowSchema(BaseModel):
    row_number: int
    seat_count: int

    @field_validator("row_number")
    @classmethod
    def validate_row_number(cls, value: int) -> int:
        if value < 0 or value > 30:
            raise ValueError("Row number must be between 0 and 30")
        return value

    @field_validator("seat_count")
    @classmethod
    def validate_seat_count(cls, value: int) -> int:
        if value < 1 or value > 6:
            raise ValueError("Seat count must be between 1 and 6")
        return value


class BusBase(BaseModel):
    """
    Base Bus Schema.
    Includes common bus fields.
    """
    bus_number: str
    license_plate: str
    bus_name: Optional[str] = None
    bus_type: BusType = BusType.STANDARD
    capacity: int
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_manufactured: Optional[int] = None
    has_wifi: bool = False
    has_ac: bool = False
    has_tv: bool = False
    has_charging_ports: bool = False
    has_refreshments: bool = False
    has_restroom: bool = False
    status: BusStatus = BusStatus.ACTIVE
    is_accessible: bool = False
    description: Optional[str] = None
    notes: Optional[str] = None

    rows: List[BusRowSchema]
    route_ids: Optional[List[UUID]] = []
    departure_ids: Optional[List[UUID]] = None
    created_by_id: Optional[UUID] = None
    operator_id: Optional[UUID] = None

    @field_validator("bus_number")
    @classmethod
    def validate_bus_number(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Bus number cannot be empty")
        return value.strip().upper()


class BusCreate(BusBase):
    """
    Schema for bus creation.
    Inherits from BusBase.
    """
    pass


class BusUpdate(BaseModel):
    """
    Schema for bus updates.
    All fields are optional.
    """
    bus_number: Optional[str] = None
    license_plate: Optional[str] = None
    bus_name: Optional[str] = None
    bus_type: Optional[BusType] = None
    capacity: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_manufactured: Optional[int] = None
    has_wifi: Optional[bool] = None
    has_ac: Optional[bool] = None
    has_tv: Optional[bool] = None
    has_charging_ports: Optional[bool] = None
    has_refreshments: Optional[bool] = None
    has_restroom: Optional[bool] = None
    status: Optional[BusStatus] = None
    is_accessible: Optional[bool] = None
    description: Optional[str] = None
    notes: Optional[str] = None

    rows: Optional[List[BusRowSchema]] = []
    route_ids: Optional[List[UUID]] = []
    departure_ids: Optional[List[UUID]] = []
    created_by_id: Optional[UUID] = None
    operator_id: Optional[UUID] = None

    @field_validator("bus_number")
    @classmethod
    def validate_bus_number(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Bus number cannot be empty")
        return value.strip().upper()


class BusResponse(BusBase):
    """
    Schema for bus responses.
    Includes id and computed fields.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amenities_list: list[str]

    departures: Optional[List] = []


class BusListItem(BaseModel):
    """
    Bus List Item Schema
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bus_number: str
    license_plate: str
    bus_name: Optional[str] = None
    bus_type: BusType
    capacity: int
    status: BusStatus
    is_accessible: bool
    amenities_list: list[str]
