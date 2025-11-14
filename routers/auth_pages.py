from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication Pages"])

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/register")
async def register_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/register/admin")
async def register_admin_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/login")
async def login_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/dashboard")
async def dashboard_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/update-profile")
async def update_profile_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )
