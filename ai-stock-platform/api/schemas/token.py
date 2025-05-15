from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[str] = None
    role: Optional[str] = None