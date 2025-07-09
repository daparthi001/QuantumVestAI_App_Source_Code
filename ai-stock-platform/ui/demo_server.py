"""
Simple demo server for QuantumVestAI UI
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import datetime

# Create FastAPI app
app = FastAPI(title="QuantumVestAI Demo")

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Mock data
portfolio = {
    "total_value": 125420.67,
    "daily_change": 2.34,
    "total_gain": 8945.32,
    "total_gain_percent": 7.68
}

periods = [
    {"value": "1D", "label": "1 Day"},
    {"value": "1W", "label": "1 Week"},
    {"value": "1M", "label": "1 Month"},
    {"value": "3M", "label": "3 Months"},
    {"value": "1Y", "label": "1 Year"}
]

market = {
    "status": "open",
    "indices": {
        "sp500": {"value": 4592.83, "change": 0.47}
    }
}

def format_currency(value):
    """Format currency values"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format percentage values"""
    return f"{value:+.2f}%"

# Add template globals
def url_for(static, path):
    """Simple url_for function for demo"""
    return f"/static{path}"

templates.env.globals.update({
    'format_currency': format_currency,
    'format_percentage': format_percentage,
    'now': datetime.datetime.now(),
    'url_for': url_for
})

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    return get_templates(request).TemplateResponse("dashboard/index.html", {
        "request": request,
        "portfolio": portfolio,
        "periods": periods,
        "selected_period": "1D",
        "market": market,
        "is_cached": False,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dark_mode": True
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "QuantumVestAI Demo Server Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)