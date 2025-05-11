from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import json
import os
import logging

router = APIRouter(prefix="/admin", tags=["admin"])

DATA_FILE = "data/admins.json"
API_KEY = os.getenv("ADMIN_API_KEY", "supersecret")  # Set in .env or environment

logging.basicConfig(level=logging.INFO)

class Admin(BaseModel):
    username: str
    name: str
    role: str

def load_admins():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_admins(admins):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(admins, f, indent=2)

def verify_api_key(request: Request):
    client_key = request.headers.get("X-API-KEY")
    if client_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")

@router.get("/health")
def health_check():
    return {"status": "Admin API is running"}

@router.get("/list", dependencies=[Depends(verify_api_key)])
def list_admins():
    return load_admins()

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