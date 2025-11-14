from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter

router = APIRouter(prefix="/routes", tags=["Routes Pages"])

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def routes_list_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/create")
async def create_route_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/{route_id}")
async def view_route_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/update/{route_id}")
async def update_route_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/delete/{route_id}")
async def delete_route_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )
