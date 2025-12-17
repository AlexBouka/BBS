import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from core.scheduler import update_delayed_departures_status
from models import Departure, DepartureStatus


@pytest.mark.asyncio
@pytest.mark.skip(reason="Scheduler tests are skipped for now")
async def test_update_delayed_departures_status(async_session: AsyncSession):
    past_time = datetime.utcnow() - timedelta(minutes=10)
    departure = Departure(
        id="test-departure-1",
        bus_id="test-bus-1",
        route_id="test-route-1",
        departure_time=past_time,
        status=DepartureStatus.SCHEDULED
    )
    async_session.add(departure)
    await async_session.commit()

    await update_delayed_departures_status()

    await async_session.refresh(departure)
    assert departure.status == DepartureStatus.DELAYED
