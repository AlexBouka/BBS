from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta, date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, distinct, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_handler import db_handler
from auth.dependencies import get_admin_user
from models import Departure, User, DepartureStatus
from schemas.departure import DepartureResponse, DepartureResponsePublic


router = APIRouter(prefix="/api/departures", tags=["Departures API"])


@router.get(
        "/by_route_id/{route_id}",
        response_model=List[DepartureResponse],
        summary="Get all departures for a route",
        description="Get all departures for a route by provided route_id"
        )
async def get_departures_for_route(
    route_id: UUID,
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get all departures for a route by provided route_id.

    Parameters:
    - route_id (UUID): The ID of the route for which to retrieve departures.

    Returns:
    - A list of DepartureResponse objects, each containing the departure details.

    Raises:
    - None
    """
    result = await session.execute(
        select(Departure)
        .options(selectinload(Departure.route))
        .where(Departure.route_id == route_id)
    )
    departures = result.scalars().all()

    if not departures:
        return []

    return departures


@router.get(
    "/",
    response_model=List[DepartureResponse],
    summary="Get all departures",
    description="Get all departures"
)
async def get_departures(
    current_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get all departures.

    Returns:
    - A list of DepartureResponse objects, each containing the departure details.

    Raises:
    - None
    """
    result = await session.execute(
        select(Departure)
        .options(selectinload(Departure.route))
        )
    departures = result.scalars().all()

    if not departures:
        return []

    return departures


@router.get(
    "/by_route/{route_id}/calendar/{year}/{month}",
    summary="Get departure dates for calendar view",
    description="Returns dates with departures for a specific month"
)
async def get_departures_for_calendar(
    route_id: UUID,
    year: int,
    month: int,
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> dict:
    # Getting first day of month
    start_date = datetime(year, month, 1)
    # Getting last day of the month (first day of next month minus 1 day)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    # Querying DB for unique departure dates
    stmt = (
        select(
            distinct(func.date(Departure.departure_time))
        ).where(
            and_(
                Departure.route_id == route_id,
                Departure.departure_time >= start_date,
                Departure.departure_time <= end_date,
                Departure.status != DepartureStatus.CANCELLED
            )
        )
    )
    result = await session.execute(stmt)
    dates = [row[0] for row in result.all()]

    return {"departure_dates": dates}


@router.get(
    "/by_route/{route_id}/upcoming",
    response_model=List[DepartureResponsePublic],
    summary="Get upcoming departures for a route",
    description="Returns all upcoming departures for a route"
)
async def get_upcoming_departures_for_route(
    route_id: UUID,
    days_ahead: int = 7,
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get upcoming departures for a route within the specified number of days.

    Parameters:
    - route_id (UUID): The ID of the route
    - days_ahead (int): Number of days to look ahead (default: 7)

    Returns:
    - List of DepartureResponse objects
    """
    now = datetime.now()
    end_date = now + timedelta(days=days_ahead)
    stmt = (
        select(Departure)
        .options(
            selectinload(Departure.route),
            selectinload(Departure.bus)
        )
        .where(
            and_(
                Departure.route_id == route_id,
                Departure.departure_time >= now,
                Departure.departure_time <= end_date,
                Departure.status != DepartureStatus.CANCELLED
            )
        )
        .order_by(Departure.departure_time)
    )
    result = await session.execute(stmt)
    departures = result.scalars().all()

    if not departures:
        return []

    return departures


@router.get(
    "/by_route/{route_id}/daily/{year}/{month}/{day}",
    response_model=List[DepartureResponsePublic],
    summary="Get departures for a specific day",
    description="Returns all departures for a specific day"
)
async def get_daily_departures(
    route_id: UUID,
    year: int,
    month: int,
    day: int,
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get all departures for a route on a specific date.

    Parameters:
    - route_id (UUID): The ID of the route
    - year (int): Year (e.g., 2025)
    - month (int): Month (1-12)
    - day (int): Day of month (1-31)

    Returns:
    - List of DepartureResponse objects for that date
    """
    # Creating date object for the specified day
    target_date = date(year, month, day)
    # Creating datetime range for the day
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    stmt = (
        select(Departure)
        .options(
            selectinload(Departure.route),
            selectinload(Departure.bus)
        )
        .where(
            and_(
                Departure.route_id == route_id,
                Departure.departure_time >= start_datetime,
                Departure.departure_time <= end_datetime,
                Departure.status != DepartureStatus.CANCELLED
            )
        )
        .order_by(Departure.departure_time)
    )
    result = await session.execute(stmt)
    departures = result.scalars().all()

    if not departures:
        return []

    return departures
