from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback

# Set up logger
logger = logging.getLogger(__name__)

# Templates setup - used for HTML error pages
templates = Jinja2Templates(directory="templates")

async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> HTMLResponse:
    """
    Handle HTTP exceptions by rendering appropriate error templates
    """
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", str(exc))

    # Handle redirects
    if status_code in (301, 302, 303, 307, 308):
        headers = getattr(exc, "headers", {})
        return HTMLResponse(
            status_code=status_code,
            headers=headers
        )
    # For API routes, return JSON response
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )
    # For UI routes, render error template
    error_template = "errors/404.html" if status_code == 404 else "errors/500.html"
    # Specific templates for common status codes
    if status_code == 401:
        error_template = "errors/401.html"
    elif status_code == 403:
        error_template = "errors/403.html"

    return templates.TemplateResponse(
        error_template,
        {
            "request": request,
            "status_code": status_code,
            "detail": detail
        },
        status_code=status_code
    )

async def handle_validation_exception(request: Request, exc: RequestValidationError) -> HTMLResponse:
    """
    Handle validation errors from request parameters
    """
    errors = exc.errors()
    error_messages = []
    for error in errors:
        loc = " -> ".join([str(x) for x in error.get("loc", [])])
        msg = error.get("msg", "")
        error_messages.append(f"{loc}: {msg}")
    detail = "\n".join(error_messages)

    # For API routes, return JSON response
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail, "errors": errors}
        )
    # For UI routes, render error template
    return templates.TemplateResponse(
        "errors/400.html",
        {
            "request": request,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": detail,
            "errors": errors
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

async def handle_not_found_exception(request: Request, exc: Exception) -> HTMLResponse:
    """
    Handle 404 Not Found errors
    """
    # For API routes, return JSON response
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The requested resource was not found"}
        )
    # For UI routes, render 404 template
    return templates.TemplateResponse(
        "errors/404.html",
        {
            "request": request,
            "status_code": status.HTTP_404_NOT_FOUND,
            "path": request.url.path
        },
        status_code=status.HTTP_404_NOT_FOUND
    )

async def handle_internal_server_error(request: Request, exc: Exception) -> HTMLResponse:
    """
    Handle 500 Internal Server Error
    """
    # Log the full error with traceback
    logger.error(
        f"Internal Server Error: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    # For API routes, return JSON response
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
    # For UI routes, render 500 template
    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

def setup_error_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI app
    """
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(404, handle_not_found_exception)
    app.add_exception_handler(500, handle_internal_server_error)
    # Catch-all handler for generic exceptions
    app.add_exception_handler(Exception, handle_internal_server_error)