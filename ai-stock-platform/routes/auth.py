from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["auth"])

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage (replace with a database in production)
users_db = {}  

def get_user(username: str):
    """Get user from database"""
    if username in users_db:
        return users_db[username]
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def get_current_user(request: Request):
    """Get current user from token in cookie"""
    token = request.cookies.get("token")
    if not token:
        return None
    username = verify_token(token)
    if username is None:
        return None
    user = get_user(username)
    return user

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid credentials"})
    
    # Create access token
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Redirect to home with cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="token", value=access_token, httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if get_user(username):
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Username already exists"})
    
    # Hash password and store user
    hashed_password = pwd_context.hash(password)
    users_db[username] = {"username": username, "password": hashed_password}
    
    return RedirectResponse(url="/login", status_code=302)

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("token")
    return response