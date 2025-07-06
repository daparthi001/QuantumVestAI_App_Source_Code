
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["predictability"])

@router.get("/predictability")
async def predictability_page(request: Request):
    """Predictability page (demo mode)"""
    return RedirectResponse(url="/login?msg=Predictability+features+require+authentication+(demo+mode)", status_code=302)

