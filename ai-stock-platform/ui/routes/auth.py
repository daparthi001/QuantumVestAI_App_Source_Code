"""
Authentication Routes for QuantumVestAI UI - API Call Version
Author: QuantumVestAI Integration
"""

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import secrets
from datetime import datetime, timedelta
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Base API URL (point to your API container service DNS or load balancer)
API_BASE_URL = os.getenv("API_BASE_URL", "http://quantumvestai-dev-api:8000/api/v1")

# UI login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

# Handle login post
@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), remember: bool = Form(False)):
    async with httpx.AsyncClient() as client:
        payload = {"username": username, "password": password}
        response = await client.post(f"{API_BASE_URL}/login-ui", json=payload)

    if response.status_code != 200:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid username or password", "username": username}, status_code=status.HTTP_401_UNAUTHORIZED)

    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid response from server"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response_redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    csrf_token = secrets.token_urlsafe(32)
    max_age = 7 * 24 * 60 * 60 if remember else None
    response_redirect.set_cookie("access_token", f"Bearer {access_token}", httponly=True, max_age=max_age, samesite="strict", secure=request.url.scheme == "https")
    response_redirect.set_cookie("csrf_token", csrf_token, httponly=False, max_age=max_age, samesite="strict", secure=request.url.scheme == "https")
    return response_redirect

# Logout route
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    return response

# Registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Handle registration post
@router.post("/register")
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Passwords don't match", "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if len(password) < 8:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Password must be at least 8 characters", "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    payload = {
        "username": username,
        "email": email,
        "password": password
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/register-ui", json=payload)

    if response.status_code != 201:
        msg = response.json().get("detail", "Registration failed")
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg, "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return templates.TemplateResponse("login.html", {"request": request, "msg": "Registration successful! Please sign in."})
