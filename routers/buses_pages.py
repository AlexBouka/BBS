from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/buses", tags=["Bus Pages"])


@router.get("/buses/create")
async def create_bus_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/buses")
async def buses_list_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/buses/{bus_id}")
async def view_bus_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/buses/update/{bus_id}")
async def update_bus_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )


@router.get("/buses/delete/{bus_id}")
async def delete_bus_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )
