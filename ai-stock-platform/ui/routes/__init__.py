# This file makes the routes directory a proper Python package.
# Updated: 2025-07-07 21:54:42
# Author: hemanth9398

# Import and expose all routers for easier imports elsewhere
try:
    from .auth import router as auth_router
except ImportError:
    auth_router = None

try:
    from .dashboard import router as dashboard_router
except ImportError:
    dashboard_router = None

try:
    from .forecast import router as forecast_router
except ImportError:
    forecast_router = None

try:
    from .market import router as market_router
except ImportError:
    market_router = None

try:
    from .watchlist import router as watchlist_router
except ImportError:
    watchlist_router = None

try:
    from .profile import router as profile_router
except ImportError:
    profile_router = None

try:
    from .predictability import router as predictability_router
except ImportError:
    predictability_router = None

try:
    from .settings import router as settings_router
except ImportError:
    settings_router = None

try:
    from .api_proxy import router as api_proxy_router
except ImportError:
    api_proxy_router = None

try:
    from .ai_api import router as ai_api_router
except ImportError:
    ai_api_router = None

try:
    from .utils import router as utils_router
except ImportError:
    utils_router = None

# List of all available routers for automatic inclusion in main app
all_routers = [
    router for router in [
        auth_router,
        dashboard_router, 
        forecast_router,
        market_router,
        watchlist_router,
        profile_router,
        predictability_router,
        settings_router,
        api_proxy_router,
        ai_api_router,
        utils_router
    ] if router is not None]
