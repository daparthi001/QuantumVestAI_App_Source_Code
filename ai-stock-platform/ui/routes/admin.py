
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["admin"])

@router.get("/admin")
async def admin_page(request: Request):
    """Admin page (demo mode)"""
    return RedirectResponse(url="/login?msg=Admin+features+require+authentication+(demo+mode)", status_code=302)

