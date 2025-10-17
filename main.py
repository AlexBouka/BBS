from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base
from core.db_handler import db_handler
from routers.auth_api import router as auth_api_router
from routers.route_api import router as route_api_router
from routers.auth_pages import router as auth_pages_router
from routers.routes_pages import router as routes_pages_router

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

    yield

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
async def add_csp_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        # Allow Swagger UI scripts and inline evaluation
        "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com 'unsafe-inline' 'unsafe-eval'; "
        # Allow Swagger UI CSS
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
        # Allow your API and Swagger to fetch resources
        "connect-src 'self' http://localhost:8000; "
        # Allow images and icons
        "img-src 'self' data:; "
    )
    return response


# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include authentication router
app.include_router(auth_api_router)
app.include_router(auth_pages_router)

# Include route router
app.include_router(route_api_router)
app.include_router(routes_pages_router)


@app.get("/")
async def root():
    """
    The root endpoint of the API.

    Returns a message welcoming the user to the Bus Booking System API.

    :return: A JSON object containing a message.
    :rtype: dict[str, str]
    """
    return {"message": "Welcome to the Bus Booking System API"}
