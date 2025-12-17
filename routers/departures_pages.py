from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter

router = APIRouter(prefix="/departures", tags=["Departures Pages"])

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/")
async def departures_list_page():
    return FileResponse(
        "frontend/static/vue/dist/index.html"
    )
