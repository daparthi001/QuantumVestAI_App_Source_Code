from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/market-data")
async def get_market_data():
    return {"status": "success", "message": "Market data endpoint is active"}
