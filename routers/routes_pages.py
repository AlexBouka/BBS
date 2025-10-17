from uuid import UUID

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request

router = APIRouter(prefix="/routes", tags=["Routes Pages"])

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def routes_list_page(request: Request):
    return templates.TemplateResponse(
        "routes-templates/route-list.html",
        {"request": request, "show_nav": True, "show_footer": True}
    )


@router.get("/create")
async def create_route_page(
        request: Request):
    return templates.TemplateResponse(
        "routes-templates/create-route.html",
        {"request": request, "show_nav": True, "show_footer": True}
    )


@router.get("/{route_id}")
async def view_route_page(request: Request, route_id: UUID):
    return templates.TemplateResponse(
        "routes-templates/route.html",
        {"request": request, "show_nav": True, "show_footer": True}
    )


@router.get("/update/{route_id}")
async def update_route_page(request: Request, route_id: UUID):
    return templates.TemplateResponse(
        "routes-templates/update-route.html",
        {"request": request, "show_nav": True, "show_footer": True}
    )


@router.get("/delete/{route_id}")
async def delete_route_page(request: Request, route_id: UUID):
    return templates.TemplateResponse(
        "routes-templates/delete-route.html",
        {"request": request, "show_nav": True, "show_footer": True}
    )
