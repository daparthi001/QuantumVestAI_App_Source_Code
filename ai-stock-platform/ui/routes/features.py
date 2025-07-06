
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["features"])

@router.get("/features")
async def features_page(request: Request):
    """Features page (demo mode)"""
    return RedirectResponse(url="/login?msg=Features+require+authentication+(demo+mode)", status_code=302)

