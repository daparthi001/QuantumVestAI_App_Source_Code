"""
Security package initialization.
"""
from .auth import *
from .encryption import *
from .permissions import *
from .rds import *
from .tokens import *
from .utils import *
from .tokens import TokenHandler

__version__ = "1.0.0"


def validate_token(token: str) -> bool:
    """Validate a JWT token. Returns True if valid, False otherwise."""
    try:
        TokenHandler.decode_token(token)
        return True
    except Exception:
        return False
