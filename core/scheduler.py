from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import update
from datetime import datetime, timedelta

from models import Departure, DepartureStatus
from core.db_handler import db_handler
from core.logging import logger
from core.config import settings

scheduler = AsyncIOScheduler()


async def update_delayed_departures_status():
    """
    Updates the status of all delayed departures to DELAYED.

    This function is used in the scheduler to periodically update the status of delayed departures.
    """
    async with db_handler.async_session_factory() as session:
        try:
            current_time = datetime.utcnow()
            threshold_time = current_time - timedelta(
                minutes=settings.schedule_delay_minutes)

            stmt = (
                update(Departure)
                .where(
                    Departure.status == DepartureStatus.SCHEDULED,
                    Departure.departure_time <= threshold_time
                )
                .values(status=DepartureStatus.DELAYED)
                .returning(Departure.id)
            )
            result = await session.execute(stmt)
            updated_ids = result.scalars().all()
            await session.commit()

            if updated_ids:
                logger.info(
                    f"Updated {len(updated_ids)} departures to DELAYED status: {updated_ids}"
                )
            else:
                logger.info("No departures needed status update on this cycle.")

        except Exception as e:
            logger.error(f"Error updating delayed departures: {e}")
            await session.rollback()


def start_scheduler():
    """
    Start the scheduler for automatic departure status updates.

    Adds a job to the scheduler to periodically update the status of delayed departures.
    The job is triggered every schedule_interval_minutes minutes
    and updates the status of all departures that are delayed by more than schedule_interval_minutes minutes to DELAYED.
    The scheduler is then started.
    """
    scheduler.add_job(
        update_delayed_departures_status,
        trigger=IntervalTrigger(
            minutes=settings.schedule_interval_minutes,
            ),
        id="update_delayed_departures_status",
        name="Update Delayed Departures Status",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started for automatic departure status updates.")


def shutdown_scheduler():
    """Shutdown the scheduler for automatic departure status updates."""
    scheduler.shutdown()
    logger.info("Scheduler shut down.")
