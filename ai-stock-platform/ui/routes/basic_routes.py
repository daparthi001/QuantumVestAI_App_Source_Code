"""
Basic Dashboard Routes for QuantumVestAI UI
Updated: 2025-07-07 21:51:56
Author: hemanth9398
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_redirect(request: Request):
    """Redirect to main dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(request: Request):
    """Basic forecast page with demo data"""
    try:
        demo_data = {
            "predictions": [
                {"symbol": "AAPL", "prediction": "bullish", "confidence": 0.85, "target_price": 195.25, "current_price": 185.50},
                {"symbol": "MSFT", "prediction": "bullish", "confidence": 0.78, "target_price": 375.50, "current_price": 365.25},
                {"symbol": "GOOGL", "prediction": "neutral", "confidence": 0.65, "target_price": 2750.00, "current_price": 2740.00},
            ]
        }
        
        return templates.TemplateResponse(
            "forecast.html",
            {
                "request": request,
                "demo_data": demo_data,
                "page_title": "AI Forecasts"
            }
        )
    except Exception as e:
        logger.error(f"Error in forecast page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>AI Forecasts - QuantumVestAI</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row">
                            <div class="col-12">
                                <h1>AI Stock Forecasts</h1>
                                <div class="alert alert-info">
                                    <h4>Demo Forecasts</h4>
                                    <p>Here are our latest AI-powered predictions:</p>
                                </div>
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">AAPL</h5>
                                                <p class="card-text">
                                                    <strong>Prediction:</strong> Bullish<br>
                                                    <strong>Confidence:</strong> 85%<br>
                                                    <strong>Target:</strong> $195.25<br>
                                                    <strong>Current:</strong> $185.50
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">MSFT</h5>
                                                <p class="card-text">
                                                    <strong>Prediction:</strong> Bullish<br>
                                                    <strong>Confidence:</strong> 78%<br>
                                                    <strong>Target:</strong> $375.50<br>
                                                    <strong>Current:</strong> $365.25
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">GOOGL</h5>
                                                <p class="card-text">
                                                    <strong>Prediction:</strong> Neutral<br>
                                                    <strong>Confidence:</strong> 65%<br>
                                                    <strong>Target:</strong> $2750.00<br>
                                                    <strong>Current:</strong> $2740.00
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                                    <a href="/market" class="btn btn-secondary">Market Data</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=200
        )

@router.get("/market", response_class=HTMLResponse)
async def market_page(request: Request):
    """Basic market page with demo data"""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Market Data - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row">
                        <div class="col-12">
                            <h1>Real-time Market Data</h1>
                            <div class="alert alert-success">
                                <h4>Market Overview</h4>
                                <p>Live market data and analytics</p>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h5 class="card-title">S&P 500</h5>
                                            <h3 class="text-success">4,756.50</h3>
                                            <p class="text-success">+1.2%</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h5 class="card-title">NASDAQ</h5>
                                            <h3 class="text-success">14,963.87</h3>
                                            <p class="text-success">+0.8%</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h5 class="card-title">DOW</h5>
                                            <h3 class="text-danger">37,123.45</h3>
                                            <p class="text-danger">-0.3%</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card text-center">
                                        <div class="card-body">
                                            <h5 class="card-title">VIX</h5>
                                            <h3>13.2</h3>
                                            <p class="text-success">-2.1%</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-4">
                                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                                <a href="/watchlist" class="btn btn-info">Watchlist</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """,
        status_code=200
    )

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist_page(request: Request):
    """Basic watchlist page"""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Watchlist - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row">
                        <div class="col-12">
                            <h1>My Watchlist</h1>
                            <div class="alert alert-info">
                                <h4>Your Tracked Stocks</h4>
                                <p>Monitor your favorite stocks and their performance</p>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Symbol</th>
                                            <th>Company</th>
                                            <th>Price</th>
                                            <th>Change</th>
                                            <th>% Change</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>AAPL</strong></td>
                                            <td>Apple Inc.</td>
                                            <td>$185.50</td>
                                            <td class="text-success">+$2.25</td>
                                            <td class="text-success">+1.23%</td>
                                            <td><button class="btn btn-sm btn-primary">View</button></td>
                                        </tr>
                                        <tr>
                                            <td><strong>MSFT</strong></td>
                                            <td>Microsoft Corp.</td>
                                            <td>$365.25</td>
                                            <td class="text-danger">-$1.50</td>
                                            <td class="text-danger">-0.41%</td>
                                            <td><button class="btn btn-sm btn-primary">View</button></td>
                                        </tr>
                                        <tr>
                                            <td><strong>GOOGL</strong></td>
                                            <td>Alphabet Inc.</td>
                                            <td>$2,750.00</td>
                                            <td class="text-success">+$15.75</td>
                                            <td class="text-success">+0.58%</td>
                                            <td><button class="btn btn-sm btn-primary">View</button></td>
                                        </tr>
                                        <tr>
                                            <td><strong>TSLA</strong></td>
                                            <td>Tesla Inc.</td>
                                            <td>$238.45</td>
                                            <td class="text-success">+$4.12</td>
                                            <td class="text-success">+1.76%</td>
                                            <td><button class="btn btn-sm btn-primary">View</button></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div class="mt-4">
                                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                                <a href="/market" class="btn btn-secondary">Market Data</a>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """,
        status_code=200
    )