from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base
from core.db_handler import db_handler
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("======== All tables created. ========")

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include authentication router
app.include_router(auth_router)


@app.get("/")
async def root():
    """
    The root endpoint of the API.

    Returns a message welcoming the user to the Bus Booking System API.

    :return: A JSON object containing a message.
    :rtype: dict[str, str]
    """
    return {"message": "Welcome to the Bus Booking System API"}
