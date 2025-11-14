from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SeatBase(BaseModel):
    seat_number: str
