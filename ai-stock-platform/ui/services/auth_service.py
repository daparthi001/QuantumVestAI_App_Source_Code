# ui/services/auth_service.py
from ui.services.api_client import APIClient
from ui.models.auth import LoginRequest

def authenticate_user(username: str, password: str):
    client = APIClient()
    response = client.authenticate(username, password)
    return response

def verify_token(token: str):
    client = APIClient(token=token)
    return client.get("/auth/verify")