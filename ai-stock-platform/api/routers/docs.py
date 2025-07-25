"""Documentation Endpoints."""
from pathlib import Path
from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/docs", tags=["docs"])

BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / "README.md").exists() and BASE_DIR != BASE_DIR.parent:
    BASE_DIR = BASE_DIR.parent
README_FILE = BASE_DIR / "README.md"
USAGE_FILE = BASE_DIR / "docs" / "API_USES.md"


@router.get("/readme", response_class=PlainTextResponse, status_code=status.HTTP_200_OK,
            summary="Get README", description="Return the repository README file")
async def get_readme() -> str:
    return README_FILE.read_text()


@router.get("/uses", response_class=PlainTextResponse, status_code=status.HTTP_200_OK,
            summary="Get usage guide", description="Return documentation usage instructions")
async def get_uses() -> str:
    if USAGE_FILE.exists():
        return USAGE_FILE.read_text()
    return "Usage documentation not found."
