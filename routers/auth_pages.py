from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request

router = APIRouter(prefix="/auth", tags=["Authentication Pages"])

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {
            "request": request, "show_nav": True, "show_footer": True
            }
        )


@router.get("/register/admin")
async def register_admin_page(request: Request):
    return templates.TemplateResponse(
        "register-admin.html", {
            "request": request, "show_nav": True, "show_footer": True
            }
        )


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {
            "request": request, "show_nav": True, "show_footer": True
            }
        )


@router.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html", {
            "request": request, "show_nav": True, "show_footer": True
            }
        )
