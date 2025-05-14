# Re-export components from routes/webapi.py, sentiment.py, and whitepaper.py
from routes.webapi import router as web_router
from routes.sentiment import router as sentiment_router
from routes.admin import router as admin_router
from routes.whitepaper_analysis import router as whitepaper_router

# Export the routers to match the import in main.py
sentiment = sentiment_router
admin = admin_router
whitepaper_analysis = whitepaper_router