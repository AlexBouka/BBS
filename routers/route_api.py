from uuid import UUID
from typing import List, Optional
from datetime import timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from models import User, Route, RouteStatus, Departure
from schemas.route import (
    RouteCreate, RouteResponse, RouteListItem,
    RouteUpdate
)
from auth.dependencies import get_admin_user
from core.db_handler import db_handler
from core.logging import logger

router = APIRouter(prefix="/api/routes", tags=["Routes API"])


@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new route",
    description="Create a new route with the provided details"
)
async def create_route(
    route_data: RouteCreate,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_admin_user)
) -> RouteResponse:
    """
    Create a new route with the provided details.

    Args:
        route_data: The RouteCreate schema containing the route details.
        session: The database session.
        current_user: The user that is creating the route (admin user).

    Returns:
        RouteResponse: The response schema containing the created route details.

    Raises:
        HTTPException: 400 if the route already exists.
        HTTPException: 500 if an unexpected error occurs during route creation.
    """
    try:
        existing_route = await session.execute(
            select(Route).where(
                func.lower(Route.route_number) == route_data.route_name.lower()
            )
        )
        if existing_route.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Route with route number {route_data.route_name} already exists."
            )

        intermediate_stops_data = None
        if route_data.intermediate_stops:
            intermediate_stops_data = [
                stop.model_dump() for stop in route_data.intermediate_stops
            ]

        new_route = Route(
            route_number=route_data.route_number,
            route_name=route_data.route_name,
            origin_city=route_data.origin_city,
            destination_city=route_data.destination_city,
            distance_km=route_data.distance_km,
            duration_minutes=route_data.duration_minutes,
            intermediate_stops=intermediate_stops_data,
            base_price=route_data.base_price,
            is_express=route_data.is_express,
            is_overnight=route_data.is_overnight,
            operates_daily=route_data.operates_daily,
            operating_days=route_data.operating_days,
            status=route_data.status,
            description=route_data.description,
            notes=route_data.notes,
            created_by_id=current_user.id
        )

        session.add(new_route)
        await session.flush()  # Get new_route.id before committing

        # Create departures if provided
        if route_data.departures:
            for departure_data in route_data.departures:
                # Calculate arrival time if not provided
                arrival_time = departure_data.arrival_time
                if not arrival_time:
                    # Add route duration to departure time
                    departure_datetime = departure_data.departure_time
                    if departure_datetime.tzinfo is None:
                        departure_datetime = departure_datetime.replace(
                            tzinfo=timezone.utc)
                    arrival_time = (
                        departure_datetime +
                        timedelta(minutes=new_route.duration_minutes)
                    )

                new_departure = Departure(
                    route_id=new_route.id,  # Assign the newly created route's ID
                    departure_time=departure_data.departure_time,
                    arrival_time=arrival_time,
                    notes=departure_data.notes
                )

                session.add(new_departure)

        await session.commit()
        await session.refresh(new_route)

        stmt = (
            select(Route)
            .options(selectinload(Route.departures))
            .where(Route.id == new_route.id)
        )
        result = await session.execute(stmt)
        new_route_with_departures = result.scalar_one()

        logger.info(f"Route: {new_route.route_number} (from {new_route.origin_city} to {new_route.destination_city}) created successfully.")

        return new_route_with_departures

    except IntegrityError as e:
        await session.rollback()
        logger.error(
            f"Database integrity error during route creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error during route creation."
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during route creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during route creation."
        )


@router.get(
    "/",
    response_model=List[RouteListItem],
    summary="Get all routes",
    description="Get a filtered and paginated list of routes"
)
async def get_routes(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    origin_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    status_filter: Optional[RouteStatus] = Query(None, alias="status"),
    session: AsyncSession = Depends(db_handler.session_dependency)
):
    """
    Get a filtered and paginated list of routes.

    Filters:
    - origin_city: the origin city of the route
    - destination_city: the destination city of the route
    - status_filter: the status of the route (ACTIVE, INACTIVE, or DELETED)

    Pagination:
    - offset: the number of routes to skip before returning the result
    - limit: the maximum number of routes to return in the result

    Returns:
    - a list of RouteListItem objects, each containing:
    the route number, route name, origin city, destination city,
    distance, estimated duration, base price, status,
    and whether the route is operational.

    Raises:
    - HTTPException: if there is an unexpected error during route retrieval.
    """
    try:
        query = select(Route)

        # Apply filters
        if origin_city:
            query = query.where(Route.origin_city == origin_city)
        if destination_city:
            query = query.where(Route.destination_city == destination_city)
        if status_filter:
            query = query.where(Route.status == status_filter)

        # Apply pagination
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        routes = result.scalars().all()

        return routes

    except Exception as e:
        logger.error(f"Unexpected error during route retrieval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during route retrieval."
        )


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Get a route by ID",
    description="Get a route by its ID"
)
async def get_route(
    route_id: UUID,
    session: AsyncSession = Depends(db_handler.session_dependency)
) -> RouteResponse:
    """
    Retrieve a route by its ID.

    Args:
        route_id (UUID): The ID of the route to retrieve.

    Returns:
        RouteResponse: The retrieved route.

    Raises:
        HTTPException: If the route with the given ID is not found.
    """
    stmt = (
        select(Route)
        .where(Route.id == route_id)
    )
    result = await session.execute(stmt)
    route = result.scalar_one_or_none()

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {route_id} not found."
        )

    return route


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Update a route by ID",
    description="Update a route by its ID"
)
async def update_route(
    route_id: UUID,
    route_data: RouteUpdate,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_admin_user)
) -> RouteResponse:
    """
    Update a route by its ID.

    Args:
        route_id (UUID): The ID of the route to update.
        route_data (RouteUpdate): The updated route data.

    Returns:
        RouteResponse: The updated route.

    Raises:
        HTTPException: If the route with the given ID is not found.
        HTTPException: If there is an unexpected error during route update.
    """
    try:
        stmt = (
            select(Route)
            .options(selectinload(Route.departures))
            .where(Route.id == route_id)
        )
        result = await session.execute(stmt)
        route = result.scalar_one_or_none()
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with ID {route_id} not found."
            )

        # Handle departures update using indices
        if hasattr(route_data, 'departures') and route_data.departures is not None:
            # Get current departures
            current_departures = route.departures or []

            # Create mapping of original indices to database departures
            original_index_to_departure = {}
            for i, dep in enumerate(current_departures):
                original_index_to_departure[i] = dep

            submitted_deps = route_data.departures or []

            # Delete departures not in submitted list
            submitted_indices = {
                dep.original_index
                for dep in submitted_deps
                if dep.original_index is not None and dep.original_index >= 0
            }
            for i, dep in enumerate(current_departures):
                if i not in submitted_indices:
                    await session.delete(dep)

            # Update existing departures and create new ones
            for submitted in submitted_deps:
                original_index = submitted.original_index

                if original_index is not None and original_index >= 0:
                    # Update existing departure
                    dep = original_index_to_departure.get(original_index)
                    if dep:
                        dep.departure_time = submitted.departure_time
                        if submitted.arrival_time is not None:
                            dep.arrival_time = submitted.arrival_time
                        else:
                            # Calculate arival_time if not provided
                            departure_datetime = submitted.departure_time
                            if departure_datetime.tzinfo is None:
                                departure_datetime = departure_datetime.replace(
                                    tzinfo=timezone.utc
                                )
                            dep.arrival_time = departure_datetime + timedelta(
                                minutes=route.duration_minutes
                            )
                        dep.notes = submitted.notes
                else:
                    # Create new departure
                    departure_time = submitted.departure_time
                    arrival_time = submitted.arrival_time
                    if arrival_time is None:
                        # Calculate arival_time if not provided
                        if departure_time.tzinfo is None:
                            departure_time = departure_time.replace(
                                tzinfo=timezone.utc
                            )
                        arrival_time = departure_time + timedelta(
                            minutes=route.duration_minutes
                        )

                    new_dep = Departure(
                        route_id=route_id,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        notes=submitted.notes
                    )
                    session.add(new_dep)

        # Update route excluding fields that are not passed
        update_data = route_data.model_dump(exclude_unset=True)

        if "intermediate_stops" in update_data and update_data["intermediate_stops"]:
            update_data["intermediate_stops"] = [
                stop.model_dump() for stop in route_data.intermediate_stops
            ]

        # Remove departures from update data to avoid conflicts
        update_data.pop("departures", None)

        # Update route
        for key, value in update_data.items():
            setattr(route, key, value)

        await session.commit()
        await session.refresh(route)

        # Re-query route to get updated departures
        requery_stmt = (
            select(Route)
            .options(selectinload(Route.departures))
            .where(Route.id == route_id)
        )

        requery_result = await session.execute(requery_stmt)
        updated_route = requery_result.scalar_one()

        logger.info(
            f"Route updated: {route.route_number} by {current_user.username}")

        return updated_route

    except HTTPException:
        await session.rollback()
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during route update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during route update."
        )


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a route by ID",
    description="Delete a route by its ID"
)
async def delete_route(
    route_id: UUID,
    session: AsyncSession = Depends(db_handler.session_dependency),
    current_user: User = Depends(get_admin_user)
) -> None:
    """
    Delete a route by its ID.

    Args:
        route_id (UUID): The ID of the route to delete.

    Returns:
        None

    Raises:
        HTTPException: If the route with the given ID is not found.
        HTTPException: If an unexpected error occurs during route deletion.
    """
    try:
        route = await session.get(Route, route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with ID {route_id} not found."
            )

        await session.delete(route)
        await session.commit()

        logger.info(
            f"Route {route.route_number} deleted by {current_user.username}.")

        return None

    except HTTPException:
        await session.rollback()
        raise

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during route deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during route deletion."
        )
