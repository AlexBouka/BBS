import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import typer

from core.config import settings
from core.database import Base
from core.db_handler import db_handler
from core.exception_handlers import (
    http_exception_handler, validation_exception_handler,
    integrity_error_handler, sqlalchemy_exception_handler,
    generic_exception_handler
)
from core.logging import logger
from core.scheduler import start_scheduler, shutdown_scheduler
from routers.auth_api import router as auth_api_router
from routers.route_api import router as route_api_router
from routers.departure_api import router as departure_api_router
from routers.bus_api import router as bus_api_router
from routers.auth_pages import router as auth_pages_router
from routers.routes_pages import router as routes_pages_router
from routers.buses_pages import router as buses_pages_router

from scripts.create_admin import create_admin_from_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycles the FastAPI application.

    Creates all tables in the database before the application starts,
    creates the admin user, and then yields control to the application.

    Once the application is finished, it drops all tables in the database.

    :param app: The FastAPI application to lifecycle.
    :type app: FastAPI
    """

    # Startup
    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("======== All tables created. ========")

    # Create admin user
    try:
        await create_admin_from_env()
    except Exception as e:
        print(f"Warning: Failed to create admin user: {e}")

    # Populate test data if requested
    if settings.populate_test_data:
        print("======== Populating test data... ========")
        try:
            from test_utils.data_populator import populate_test_data
            await populate_test_data()
            print("======== Test data populated successfully! ========")
        except Exception as e:
            print(f"Warning: Failed to populate test data: {e}")

    # Start scheduler
    start_scheduler()

    yield

    # Shutdown scheduler
    shutdown_scheduler()

    # Shutdown
    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("======== All tables dropped. ========")


app = FastAPI(
    title="Bus Booking System API",
    description="API for managing bus bookings, users, and schedules.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

origins = ["http://localhost:8000"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        # Allow Swagger UI scripts and inline evaluation
        "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com 'unsafe-inline' 'unsafe-eval'; "
        # Allow Swagger UI CSS
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
        # Allow API and Swagger to fetch resources
        "connect-src 'self' http://localhost:8000; "
        # Allow images and icons
        "img-src 'self' data:; "
    )
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Logs incoming HTTP requests with their method, path, status code, and
    processing time.

    This middleware is useful for debugging and monitoring the API.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.2f}ms"
    )
    return response


# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Serve static files (CSS, JS)
app.mount(
    "/static", StaticFiles(directory="frontend/static"), name="static")

# Serve Vue app
app.mount(
    "/vue", StaticFiles(directory="frontend/static/vue/dist"), name="vue")

# Include authentication router
app.include_router(auth_api_router)
app.include_router(auth_pages_router)

# Include route router
app.include_router(route_api_router)
app.include_router(routes_pages_router)

# Include departure router
app.include_router(departure_api_router)

# Include bus router
app.include_router(bus_api_router)
app.include_router(buses_pages_router)


@app.get("/")
async def root():
    """
    The root endpoint of the API.

    Returns a message welcoming the user to the Bus Booking System API.

    :return: A JSON object containing a message.
    :rtype: dict[str, str]
    """
    return {"message": "Welcome to the Bus Booking System API"}


# CLI command for populating test data
cli_app = typer.Typer()


@cli_app.command()
def populate_test_data():
    """Populate the database with test data."""
    print("Populating test data...")
    from test_utils.data_populator import populate_test_data
    asyncio.run(populate_test_data())
    print("Test data populated successfully!")


@cli_app.command()
def dev():
    """Run the FastAPI development server."""
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    cli_app()
