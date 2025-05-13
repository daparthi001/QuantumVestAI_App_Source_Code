from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
import logging
import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="templates")
DATA_FILE = "data/admins.json"
MODEL_INFO_FILE = "data/model_info.json"
API_KEY = os.getenv("ADMIN_API_KEY", "supersecret")  # Set in .env or environment

logging.basicConfig(level=logging.INFO)

class Admin(BaseModel):
    username: str
    name: str
    role: str

def verify_api_key(request: Request):
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")

def load_admins():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_admins(admins):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(admins, f, indent=2)

def load_model_info():
    if not os.path.exists(MODEL_INFO_FILE):
        # Default model info if file doesn't exist
        return {
            "AAPL": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d"), "model": "Ensemble"},
            "MSFT": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d"), "model": "XGBoost"},
            "GOOG": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d"), "model": "Prophet"}
        }
    with open(MODEL_INFO_FILE, "r") as f:
        return json.load(f)

@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    model_info = load_model_info()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "models": model_info})

@router.get("/health")
def health_check():
    return {"status": "Admin API is running"}

@router.get("/list", dependencies=[Depends(verify_api_key)])
def list_admins():
    return load_admins()

@router.get("/models", dependencies=[Depends(verify_api_key)])
def list_models():
    return load_model_info()

@router.get("/{username}", dependencies=[Depends(verify_api_key)])
def get_admin(username: str):
    admins = load_admins()
    if username not in admins:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admins[username]

@router.post("/add", dependencies=[Depends(verify_api_key)])
def add_admin(admin: Admin):
    admins = load_admins()
    if admin.username in admins:
        raise HTTPException(status_code=400, detail="Admin already exists")
    admins[admin.username] = admin.dict()
    save_admins(admins)
    logging.info(f"Admin added: {admin.username}")
    return {"message": f"Admin '{admin.username}' added successfully."}

@router.delete("/remove/{username}", dependencies=[Depends(verify_api_key)])
def remove_admin(username: str):
    admins = load_admins()
    if username not in admins:
        raise HTTPException(status_code=404, detail="Admin not found")
    del admins[username]
    save_admins(admins)
    logging.info(f"Admin removed: {username}")
    return {"message": f"Admin '{username}' removed successfully."}

@router.post("/retrain", dependencies=[Depends(verify_api_key)])
def trigger_retrain(ticker: str = Form(...), model_type: str = Form(...)):
    try:
        # In a real application, you would trigger an async task here
        # For now, we'll just update the model info
        model_info = load_model_info()
        if ticker not in model_info:
            model_info[ticker] = {}
            
        model_info[ticker]["model"] = model_type
        model_info[ticker]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Save updated model info
        os.makedirs(os.path.dirname(MODEL_INFO_FILE), exist_ok=True)
        with open(MODEL_INFO_FILE, "w") as f:
            json.dump(model_info, f, indent=2)
            
        logging.info(f"Model retrain triggered for {ticker} using {model_type}")
        return {"message": f"Retrain triggered for {ticker} using {model_type}"}
    except Exception as e:
        logging.error(f"Error triggering retrain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger retrain: {str(e)}")