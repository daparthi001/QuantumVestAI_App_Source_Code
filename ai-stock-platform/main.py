from fastapi import FastAPI
from routes.sentiment import router as sentiment
from routes.admin import router as admin
from routes.whitepaper_analysis import router as whitepaper_analysis

app = FastAPI()

app.include_router(sentiment)
app.include_router(admin)
app.include_router(whitepaper_analysis)

# Add a health check endpoint
@app.get("/health")
async def health():
    """Simple health check endpoint for monitoring services"""
    return {"status": "ok", "service": "ai-stock-platform", "version": "1.0.0"}