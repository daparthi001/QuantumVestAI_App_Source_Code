#!/usr/bin/env python3
"""
Fix Route Loading Issues in QuantumVestAI UI
Created: 2025-08-04
"""
import importlib
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("route_fixer")

def fix_routes():
    """Diagnose and fix route loading issues"""
    logger.info("Starting route diagnosis")
    
    # Add necessary paths
    sys_paths = [
        os.path.abspath("."),  # Current directory
        os.path.abspath(".."),  # Parent directory
        os.path.abspath("../.."),  # Grandparent directory
    ]
    
    for path in sys_paths:
        if path not in sys.path:
            sys.path.insert(0, path)
            logger.info(f"Added path to sys.path: {path}")
    
    # Try to import the ai_api module
    try:
        # Try relative import first
        logger.info("Attempting to import from routes.ai_api")
        from routes import ai_api
        logger.info("✅ Successfully imported routes.ai_api")
        has_router = hasattr(ai_api, "router")
        logger.info(f"  Has router: {has_router}")
        if has_router:
            logger.info(f"  Router path: {ai_api.router.prefix}")
            logger.info(f"  Number of routes: {len(ai_api.router.routes)}")
    except ImportError:
        logger.error("❌ Failed to import routes.ai_api")
        
        # Try ui.routes.ai_api
        try:
            logger.info("Attempting to import from ui.routes.ai_api")
            from ui.routes import ai_api as ui_ai_api
            logger.info("✅ Successfully imported ui.routes.ai_api")
            has_router = hasattr(ui_ai_api, "router")
            logger.info(f"  Has router: {has_router}")
            if has_router:
                logger.info(f"  Router path: {ui_ai_api.router.prefix}")
                logger.info(f"  Number of routes: {len(ui_ai_api.router.routes)}")
        except ImportError:
            logger.error("❌ Failed to import ui.routes.ai_api")
            
            # Try direct import from file
            try:
                logger.info("Attempting direct import from file")
                import imp
                ai_api_path = os.path.join(os.path.dirname(__file__), "routes", "ai_api.py")
                if os.path.exists(ai_api_path):
                    ai_api_module = imp.load_source("ai_api", ai_api_path)
                    logger.info("✅ Successfully imported ai_api directly from file")
                    has_router = hasattr(ai_api_module, "router")
                    logger.info(f"  Has router: {has_router}")
                    if has_router:
                        logger.info(f"  Router path: {ai_api_module.router.prefix}")
                else:
                    logger.error(f"❌ File not found: {ai_api_path}")
            except Exception as e:
                logger.error(f"❌ Failed to import directly: {e}")
    
    # Check that the router is registered in __init__.py
    try:
        logger.info("Checking routes/__init__.py for ai_api_router")
        from routes import __init__ as routes_init
        if hasattr(routes_init, "ai_api_router"):
            logger.info("✅ ai_api_router found in routes/__init__.py")
        else:
            logger.error("❌ ai_api_router not found in routes/__init__.py")
            logger.info("Attempting to fix routes/__init__.py")
            
            # Create a simple fix by copying the router
            try:
                from routes import ai_api
                if not hasattr(routes_init, "ai_api_router") and hasattr(ai_api, "router"):
                    routes_init.ai_api_router = ai_api.router
                    if hasattr(routes_init, "all_routers") and isinstance(routes_init.all_routers, list):
                        routes_init.all_routers.append(ai_api.router)
                        logger.info("✅ Added ai_api.router to routes_init.all_routers")
                    logger.info("✅ Created ai_api_router in routes/__init__.py")
            except Exception as e:
                logger.error(f"❌ Failed to fix routes/__init__.py: {e}")
    except ImportError:
        logger.error("❌ Failed to import routes/__init__.py")
    
    logger.info("Route diagnosis complete")

if __name__ == "__main__":
    fix_routes()
