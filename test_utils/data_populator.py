import asyncio
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_handler import db_handler
from models import (
    User, UserRole,
    Route, RouteStatus,
    Departure, DepartureStatus,
    Bus, BusStatus, BusType)
from auth.pass_utils import pwd_utils

fake = Faker()


async def create_test_users(
        session: AsyncSession, num_users: int = 10) -> list[User]:
    """Create test users with one admin."""
    users = []
    admin_created = False

    for i in range(num_users):
        role = UserRole.ADMIN if not admin_created and i == 0 else UserRole.CUSTOMER
        if role == UserRole.ADMIN:
            admin_created = True

        user = User(
            username=fake.user_name() + str(i),
            email=fake.email(),
            password_hash=pwd_utils.hash_password("password123"),
            role=role,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            is_active=True,
            is_verified=True
        )
        session.add(user)
        users.append(user)

    await session.commit()
    for user in users:
        await session.refresh(user)

    print(f"Created {len(users)} test users (1 admin, {len(users)-1} customers)")
    return users


async def create_test_routes(
        session: AsyncSession, admin_user: User, num_routes: int = 10
        ) -> list[Route]:
    """Create test routes under admin user."""
    routes = []

    for i in range(num_routes):
        route = Route(
            route_number=f"R{i+1:03d}",
            route_name=fake.city() + " Express",
            origin_city=fake.city(),
            destination_city=fake.city(),
            distance_km=fake.random_int(100, 1000),
            duration_minutes=fake.random_int(120, 600),
            base_price=round(fake.random_number(digits=2) + fake.random_number(digits=1) / 100, 2),
            status=RouteStatus.ACTIVE,
            is_express=fake.boolean(),
            is_overnight=fake.boolean(),
            operates_daily=fake.boolean(),
            operating_days=["monday", "wednesday", "friday"] if not fake.boolean() else None,
            description=fake.text(max_nb_chars=200),
            notes=fake.text(max_nb_chars=100),
            created_by_id=admin_user.id
        )
        session.add(route)
        routes.append(route)

    await session.commit()
    for route in routes:
        await session.refresh(route)

    print(f"Created {len(routes)} test routes under admin user")
    return routes


async def create_test_departures(
        session: AsyncSession, routes: list[Route], departures_per_route: int = 10
        ) -> list[Departure]:
    """Create test departures for each route with one day intervals."""
    departures = []
    base_time = datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0)

    for route in routes:
        for i in range(departures_per_route):
            departure_time = base_time + timedelta(days=i)
            arrival_time = departure_time + timedelta(minutes=route.duration_minutes)

            departure = Departure(
                route_id=route.id,
                departure_time=departure_time,
                arrival_time=arrival_time,
                status=DepartureStatus.SCHEDULED,
                notes=fake.text(max_nb_chars=50) if fake.boolean() else None
            )
            session.add(departure)
            departures.append(departure)

    await session.commit()
    for departure in departures:
        await session.refresh(departure)

    print(f"Created {len(departures)} test departures ({departures_per_route} per route)")
    return departures


async def create_test_buses(
        session: AsyncSession, departures: list[Departure], admin_user: User
        ) -> list[Bus]:
    """Create one bus per departure, assigned to the departure's route."""
    from models.bus_route import BusRoute  # Import here to avoid circular imports
    buses = []

    for i, departure in enumerate(departures):
        bus = Bus(
            bus_number=f"BUS{i+1:04d}",
            license_plate=fake.license_plate(),
            bus_name=f"{fake.company()} {fake.random_element(['Express', 'Luxury', 'Standard'])}",
            bus_type=fake.random_element(list(BusType)),
            capacity=fake.random_int(20, 60),
            manufacturer=fake.company(),
            model=fake.random_element(["Model A", "Model B", "Model C"]),
            year_manufactured=fake.random_int(2010, 2023),
            has_wifi=fake.boolean(),
            has_ac=fake.boolean(),
            has_tv=fake.boolean(),
            has_charging_ports=fake.boolean(),
            has_refreshments=fake.boolean(),
            has_restroom=fake.boolean(),
            status=BusStatus.ACTIVE,
            is_accessible=fake.boolean(),
            description=fake.text(max_nb_chars=150),
            notes=fake.text(max_nb_chars=100),
            created_by_id=admin_user.id,
            operator_id=admin_user.id
        )
        session.add(bus)
        buses.append(bus)

    await session.commit()
    for bus in buses:
        await session.refresh(bus)

    # Create bus-route associations and assign buses to departures
    for bus, departure in zip(buses, departures):
        # Create BusRoute association
        bus_route = BusRoute(
            bus_id=bus.id,
            route_id=departure.route_id
        )
        session.add(bus_route)

        # Assign bus to departure
        departure.bus_id = bus.id

    await session.commit()

    print(f"Created {len(buses)} test buses, assigned to departures, and linked to routes via bus_routes")
    return buses


async def populate_test_data():
    """Main function to populate test data."""
    session = db_handler.get_scoped_session()
    try:
        print("Starting test data population...")

        # 1. Create users (1 admin, 9 customers)
        users = await create_test_users(session, 10)
        admin_user = next(user for user in users if user.role == UserRole.ADMIN)

        # 2. Create routes under admin
        routes = await create_test_routes(session, admin_user, 10)

        # 3. Create departures for each route (10 per route)
        departures = await create_test_departures(session, routes, 10)

        # 4. Create buses and assign to departures
        buses = await create_test_buses(session, departures, admin_user)

        print("Test data population completed!")
        print(f"Summary: {len(users)} users, {len(routes)} routes, {len(departures)} departures, {len(buses)} buses")

    finally:
        await session.remove()

if __name__ == "__main__":
    asyncio.run(populate_test_data())
