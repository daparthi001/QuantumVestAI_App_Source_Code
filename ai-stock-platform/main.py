from fastapi import FastAPI
from routes.sentiment import router as sentiment
from routes.admin import router as admin
from routes.whitepaper_analysis import router as whitepaper_analysis

app = FastAPI()

app.include_router(sentiment)
app.include_router(admin)
app.include_router(whitepaper_analysis)

# Add health check endpoint required by Kubernetes liveness and readiness probes
@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    return {"status": "ok", "service": "QuantumVestAI", "version": "1.0.0"}