<<<<<<< HEAD
"""
QuantumVestAI UI Routes Package
Updated: 2025-07-07 21:49:53
Author: hemanth9398

This package contains all route modules for the QuantumVestAI UI application.
All route files have been fixed and updated with comprehensive functionality.
"""
=======
# This file makes the routes directory a proper Python package.
# Updated: 2025-07-07 21:54:42
# Author: hemanth9398
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

# Import and expose all routers for easier imports elsewhere
try:
    from routes.auth import router as auth_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import auth router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    auth_router = None

try:
    from routes.dashboard import router as dashboard_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import dashboard router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    dashboard_router = None

try:
    from routes.forecast import router as forecast_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import forecast router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    forecast_router = None

try:
    from routes.market import router as market_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import market router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    market_router = None

try:
    from routes.watchlist import router as watchlist_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import watchlist router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    watchlist_router = None

try:
    from routes.predictability import router as predictability_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import predictability router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    predictability_router = None

try:
    from routes.settings import router as settings_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import settings router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    settings_router = None

try:
    from routes.api_proxy import router as api_proxy_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import api_proxy router: {e}")
=======
except ImportError:
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    api_proxy_router = None

try:
    from routes.utils import router as utils_router
<<<<<<< HEAD
except ImportError as e:
    print(f"Warning: Could not import utils router: {e}")
    utils_router = None

try:
    from routes.admin import router as admin_router
except ImportError as e:
    print(f"Warning: Could not import admin router: {e}")
    admin_router = None
=======
except ImportError:
    utils_router = None
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

# List of all available routers for automatic inclusion in main app
# Filter out None values from failed imports
all_routers = [
    router for router in [
        auth_router,
        dashboard_router, 
        forecast_router,
        market_router,
<<<<<<< HEAD
        watchlist_router,
        predictability_router,
        settings_router,
        api_proxy_router,
        utils_router,
        admin_router
    ] if router is not None
]

# Route configuration metadata
route_metadata = {
    "auth": {
        "prefix": "",
        "tags": ["auth"],
        "description": "Authentication and user management routes"
    },
    "dashboard": {
        "prefix": "/dashboard",
        "tags": ["dashboard"],
        "description": "Dashboard and portfolio management routes"
    },
    "forecast": {
        "prefix": "/forecast",
        "tags": ["forecast"],
        "description": "AI forecasting and prediction routes"
    },
    "market": {
        "prefix": "/market",
        "tags": ["market"],
        "description": "Market data and analysis routes"
    },
    "watchlist": {
        "prefix": "/watchlist",
        "tags": ["watchlist"],
        "description": "Watchlist management routes"
    },
    "predictability": {
        "prefix": "/predictability",
        "tags": ["predictability"],
        "description": "Stock predictability analysis routes"
    },
    "settings": {
        "prefix": "/settings",
        "tags": ["settings"],
        "description": "User settings and preferences routes"
    },
    "api_proxy": {
        "prefix": "/api",
        "tags": ["api_proxy"],
        "description": "API proxy and backend integration routes"
    },
    "utils": {
        "prefix": "/utils",
        "tags": ["utilities"],
        "description": "Utility and helper function routes"
    },
    "admin": {
        "prefix": "/admin",
        "tags": ["admin"],
        "description": "Administrative routes and functions"
    }
}

print(f"Successfully loaded {len(all_routers)} route modules")

__all__ = [
    "auth_router",
    "dashboard_router", 
    "forecast_router",
    "market_router",
    "watchlist_router",
    "predictability_router",
    "settings_router",
    "api_proxy_router",
    "utils_router",
    "admin_router",
    "all_routers",
    "route_metadata"
=======
        watchlist_router, 
        predictability_router,
        settings_router,
        api_proxy_router,
        utils_router
    ] if router is not None
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
]