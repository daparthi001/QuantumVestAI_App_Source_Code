"""
Application startup configuration for QuantumVestAI UI
Handles HTTP client initialization and cleanup.

Last updated: 2025-01-18
Updated by: daparthi001
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for proper HTTP client initialization and cleanup.
    """
    # Startup
    logger.info("Starting QuantumVestAI UI application...")
    
    try:
        # Initialize HTTP client configuration
        from core.http_client import HTTPClientConfig, get_http_client

        # Test HTTP client initialization
        async with get_http_client() as client:
            logger.info("HTTP client initialized successfully")
            logger.info(f"Connection pooling: max_connections={client.config.limits.max_connections}, "
                       f"max_keepalive={client.config.limits.max_keepalive_connections}")
            logger.info(f"Timeouts: connect={client.config.timeout.connect}s, "
                       f"read={client.config.timeout.read}s")
            logger.info(f"Retries: max_retries={client.config.max_retries}")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down QuantumVestAI UI application...")
    
    try:
        # Cleanup HTTP clients
        from core.http_client import cleanup_http_clients
        await cleanup_http_clients()
        logger.info("HTTP clients cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")
    
    logger.info("Application shutdown completed")

def configure_logging():
    """Configure application logging."""
    import os
    
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    if debug_mode:
        log_level = "DEBUG"
    
    # Configure logging format
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Set httpx logging level (it can be quite verbose)
    httpx_logger = logging.getLogger("httpx")
    if log_level == "DEBUG":
        httpx_logger.setLevel(logging.DEBUG)
    else:
        httpx_logger.setLevel(logging.WARNING)
    
    # Set httpcore logging level
    httpcore_logger = logging.getLogger("httpcore")
    if log_level == "DEBUG":
        httpcore_logger.setLevel(logging.DEBUG)
    else:
        httpcore_logger.setLevel(logging.WARNING)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # Configure logging first
    configure_logging()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="QuantumVestAI UI",
        description="Advanced AI-powered investment platform UI",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add HTTP client configuration to app state
    try:
        from core.http_client import HTTPClientConfig
        app.state.http_config = HTTPClientConfig()
        logger.info("HTTP client configuration added to app state")
    except Exception as e:
        logger.warning(f"Could not add HTTP config to app state: {e}")
    
    return app

# Health check endpoint for monitoring
async def health_check():
    """
    Health check endpoint that verifies HTTP client functionality.
    """
    try:
        from core.http_client import get_http_client

        # Test HTTP client
        async with get_http_client() as client:
            # Basic health check - just verify client creation
            health_status = {
                "status": "healthy",
                "http_client": "operational",
                "timestamp": "2025-01-18T12:00:00Z"
            }
            
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-01-18T12:00:00Z"
        }

# Example of how to add the health check to your FastAPI app
def add_health_endpoints(app: FastAPI):
    """Add health check endpoints to the FastAPI app."""
    
    @app.get("/health")
    async def get_health():
        """Basic health check endpoint."""
        return await health_check()
    
    @app.get("/health/http")
    async def get_http_health():
        """HTTP client specific health check."""
        try:
            from core.http_client import HTTPClientConfig, get_http_client
            
            config = HTTPClientConfig()
            async with get_http_client() as client:
                return {
                    "status": "healthy",
                    "http_client": {
                        "max_connections": config.limits.max_connections,
                        "max_keepalive": config.limits.max_keepalive_connections,
                        "connect_timeout": config.timeout.connect,
                        "read_timeout": config.timeout.read,
                        "max_retries": config.max_retries,
                        "ssl_verify": config.verify_ssl
                    },
                    "timestamp": "2025-01-18T12:00:00Z"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-18T12:00:00Z"
            }

if __name__ == "__main__":
    # Example of how to run the application
    import os

    import uvicorn
    
    app = create_app()
    add_health_endpoints(app)
    
    # Run the application
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
