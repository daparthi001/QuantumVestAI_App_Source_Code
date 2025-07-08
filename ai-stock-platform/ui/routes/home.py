from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=Path("templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):    return get_templates(request).TemplateResponse("home.html", {"request": request})