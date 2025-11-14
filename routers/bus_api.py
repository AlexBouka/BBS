import string
from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from models import User, Bus, BusType, BusStatus, BusRoute, Seat, Departure
from schemas.bus import (
    BusCreate, BusResponse,
    BusUpdate, BusListItem
)
from auth.dependencies import get_admin_user
from core.db_handler import db_handler
from core.logging import logger

router = APIRouter(prefix="/api/buses", tags=["Buses API"])


@router.post(
    "/",
    response_model=BusResponse,
    summary="Create a new bus",
    description="Create a new bus with the provided details"
)
async def create_bus(
    bus_data: BusCreate,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new bus with the provided details.

    Args:
        bus_data: The BusCreate schema containing the bus details.
        session: The database session.
        current_user: The user that is creating the bus (admin user).

    Returns:
        BusResponse: The response schema containing the created bus details.

    Raises:
        HTTPException: 400 if the bus already exists.
        HTTPException: 500 if an unexpected error occurs during bus creation.
    """
    try:
        existing_bus = await session.execute(
            select(Bus).where(
                Bus.bus_number == bus_data.bus_number
            )
        )
        if existing_bus.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Bus with bus number {bus_data.bus_number} "
                    "already exists."
                )
            )

        new_bus = Bus(
            bus_number=bus_data.bus_number,
            license_plate=bus_data.license_plate,
            bus_name=bus_data.bus_name,
            bus_type=bus_data.bus_type,
            capacity=bus_data.capacity,
            manufacturer=bus_data.manufacturer,
            model=bus_data.model,
            year_manufactured=bus_data.year_manufactured,
            has_wifi=bus_data.has_wifi,
            has_ac=bus_data.has_ac,
            has_tv=bus_data.has_tv,
            has_charging_ports=bus_data.has_charging_ports,
            has_refreshments=bus_data.has_refreshments,
            has_restroom=bus_data.has_restroom,
            status=bus_data.status,
            is_accessible=bus_data.is_accessible,
            description=bus_data.description,
            notes=bus_data.notes,
            route_id=bus_data.route_id,
            departure_id=bus_data.departure_id,
            created_by_id=current_user.id,
        )
        session.add(new_bus)
        await session.flush()  # get new_bus.id before adding seats

        # Generate seats based on provided rows
        alphabet = list(string.ascii_uppercase)
        for row in bus_data.rows:
            for i in range(row.seat_count):
                seat_label = alphabet[i]
                seat_number = f"{row.row_number}{seat_label}"
                seat = Seat(bus_id=new_bus.id, seat_number=seat_number)
                session.add(seat)

        await session.commit()
        await session.refresh(new_bus)

        return new_bus

    except IntegrityError as e:
        await session.rollback()
        logger.error(
            f"Database integrity error during bus creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error during bus creation."
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during bus creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during bus creation."
        )


@router.get(
    "/",
    response_model=List[BusListItem],
    summary="Get all buses",
    description="Get a list of all buses"
)
async def get_buses(
    offset: int = Query(0, ge=0),
    limit: int = Query(16, ge=1, le=100),
    bus_number: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    bus_type: Optional[BusType] = Query(None, alias="type"),
    status_filter: Optional[BusStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get a list of all buses.

    Parameters:
    - offset: The number of buses to skip before returning the result.
    - limit: The maximum number of buses to return in the result.
    - bus_number: Filter by bus number.
    - manufacturer: Filter by manufacturer.
    - model: Filter by model.
    - bus_type: Filter by bus type (e.g. STANDARD, EXECUTIVE, etc.).
    - status_filter: Filter by status (e.g. ACTIVE, INACTIVE, DELETED, etc.).

    Returns:
    - a list of BusListItem objects, each containing:
    the bus number, license plate, bus name, bus type,
    capacity, distance, estimated duration, base price,
    status, is accessible, description, notes.

    Raises:
    - HTTPException: if there is an unexpected error during bus retrieval.
    """
    try:
        query = select(Bus)

        # Apply filters
        if bus_number:
            query = query.where(Bus.bus_number == bus_number)
        if manufacturer:
            query = query.where(Bus.manufacturer == manufacturer)
        if model:
            query = query.where(Bus.model == model)
        if bus_type:
            query = query.where(Bus.bus_type == bus_type)
        if status_filter:
            query = query.where(Bus.status == status_filter)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        buses = result.scalars().all()

        return buses

    except Exception as e:
        logger.error(f"Unexpected error during bus retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during bus retrieval."
        )


@router.get(
    "/{bus_id}",
    response_model=BusResponse,
    summary="Get a bus by ID",
    description="Get a bus by its ID"
)
async def get_bus(
    bus_id: UUID,
    current_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get a bus by its ID.

    Parameters:
    - bus_id (UUID): The ID of the bus to retrieve.

    Returns:
    - a BusResponse object containing the bus details.

    Raises:
    - HTTPException: if the bus with the given ID is not found.
    """
    stmt = (
        select(Bus)
        .options(
            selectinload(Bus.departures).selectinload(Departure.route),
            selectinload(Bus.departures).selectinload(Departure.bus))  # Load Bus for computed fields (even if redundant)
        .where(Bus.id == bus_id)
    )
    result = await session.execute(stmt)
    bus = result.scalar_one_or_none()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus with ID {bus_id} not found."
        )

    return bus


@router.put(
    "/{bus_id}",
    response_model=BusResponse,
    summary="Update a bus by ID",
    description="Update a bus by its ID"
)
async def update_bus(
    bus_id: UUID,
    bus_data: BusUpdate,
    current_user: User = Depends(get_admin_user),
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Update a bus by its ID.

    Parameters:
    - bus_id (UUID): The ID of the bus to update.
    - bus_data (BusUpdate): The bus data to update.

    Returns:
    - a BusResponse object containing the bus details.

    Raises:
    - HTTPException: if the bus with the given ID is not found.
    - HTTPException: if the bus with the given number already exists.
    - HTTPException: if the bus with the given ID does not belong to an assigned route.
    - HTTPException: if there is an unexpected error during bus retrieval.
    """
    try:
        bus = await session.get(Bus, bus_id)

        if not bus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bus with ID {bus_id} not found."
            )

        if bus_data.bus_number and bus_data.bus_number != bus.bus_number:
            stmt = select(Bus).where(Bus.bus_number == bus_data.bus_number)
            existing_bus = await session.execute(stmt)
            if existing_bus.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bus with number {bus_data.bus_number} already exists."
                )

        updates = {
            key: value for key, value in bus_data.model_dump(exclude_unset=True).items() if value is not None
        }
        for key, value in updates.items():
            setattr(bus, key, value)

        # Handle route ids
        if hasattr(bus_data, 'route_ids') and bus_data.route_ids is not None:
            await session.execute(delete(BusRoute).where(BusRoute.bus_id == bus_id))

            for route_id in bus_data.route_ids:
                bus_route = BusRoute(bus_id=bus_id, route_id=route_id)
                session.add(bus_route)

        # Handle departure ids
        if hasattr(bus_data, 'departure_ids') and bus_data.departure_ids:
            # Validate that departures belong to assigned routes
            if hasattr(bus_data, 'route_ids') and bus_data.route_ids:
                for departure_id in bus_data.departure_ids:
                    departure = await session.get(Departure, departure_id)
                    if not departure or departure.route_id not in bus_data.route_ids:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Departure {departure_id} does not belong to an assigned route."
                        )

            # Clear existing bus assignments for these departures
            await session.execute(
                update(Departure).where(
                    Departure.id.in_(bus_data.departure_ids)
                ).values(bus_id=None)
            )

            for departure_id in bus_data.departure_ids:
                departure = await session.get(Departure, departure_id)
                departure.bus_id = bus_id
                session.add(departure)

        # Handle rows (seats update)
        if bus_data.rows is not None:
            # Delete existing seats
            await session.execute(
                select(Seat).where(Seat.bus_id == bus_id).delete()
            )
            # Add new seats
            alphabet = list(string.ascii_uppercase)
            for row in bus_data.rows:
                for i in range(row.seat_count):
                    seat_label = alphabet[i]
                    seat_number = f"{row.row_number}{seat_label}"
                    seat = Seat(bus_id=bus_id, seat_number=seat_number)
                    session.add(seat)

        await session.commit()
        await session.refresh(bus)

        logger.info(
            f"Bus {bus_id} updated by user {current_user.username} | {current_user.id}")

        return bus

    except HTTPException:
        await session.rollback()
        raise

    except IntegrityError as e:
        logger.error(f"Database integrity error during bus update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error during bus update."
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during bus update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during bus update."
        )
