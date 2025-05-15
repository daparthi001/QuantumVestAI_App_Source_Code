# This file makes the routes directory a proper Python package.
# It can include route-specific initializations or expose key components.

# Import and expose all routers for easier imports elsewhere
from ui.routes.auth import router as auth_router
from ui.routes.forecast import router as forecast_router
from ui.routes.admin import router as admin_router
from ui.routes.watchlist import router as watchlist_router
from ui.routes.predictability import router as predictability_router

# List of all available routers for automatic inclusion in main app
all_routers = [
    auth_router, 
    forecast_router,
    admin_router,
    watchlist_router, 
    predictability_router
]