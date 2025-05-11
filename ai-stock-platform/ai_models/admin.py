from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dummy data (replace with real DB/model calls)
model_info = {
    "AAPL": {"last_updated": "2025-05-10", "model": "Ensemble"},
    "MSFT": {"last_updated": "2025-05-09", "model": "XGBoost"},
    "GOOG": {"last_updated": "2025-05-08", "model": "Prophet"}
}

@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "models": model_info})
