"""
API Error Handler Middleware
Created: 2025-06-19 03:05:06
Enhanced: 2025-01-09 (AI Assistant)
Author: daparthi001
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
import uuid
from typing import Callable

from ..exceptions import APIException
from ..responses import create_error_response

logger = logging.getLogger("api")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Enhanced error handler middleware with standardized responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
        except APIException as e:
            # Handle custom API exceptions
            logger.error(f"API Exception [{request_id}]: {str(e)}")
            
            error_response = create_error_response(
                message=e.detail,
                error_code=getattr(e, 'error_code', None),
                request_id=request_id
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content=error_response,
                headers=e.headers
            )
        
        except RequestValidationError as e:
            # Handle Pydantic validation errors
            logger.error(f"Validation Error [{request_id}]: {str(e)}")
            
            error_details = {
                "validation_errors": [
                    {
                        "field": ".".join(str(loc) for loc in error.get("loc", [])),
                        "message": error.get("msg", ""),
                        "type": error.get("type", "")
                    }
                    for error in e.errors()
                ]
            }
            
            error_response = create_error_response(
                message="Request validation failed",
                error_code="VALIDATION_ERROR",
                details=error_details,
                request_id=request_id
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response
            )
        
        except ValueError as e:
            # Handle value errors
            logger.error(f"Value Error [{request_id}]: {str(e)}")
            
            error_response = create_error_response(
                message="Invalid input value",
                error_code="VALUE_ERROR",
                details={"original_error": str(e)},
                request_id=request_id
            )
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response
            )
        
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Unhandled Exception [{request_id}]: {str(e)}")
            logger.error(f"Traceback [{request_id}]: {traceback.format_exc()}")
            
            # Don't expose internal error details in production
            error_message = "An internal server error occurred"
            error_details = None
            
            # In development, include more details
            if hasattr(request.app, 'debug') and request.app.debug:
                error_message = str(e)
                error_details = {
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc().split('\n')
                }
            
            error_response = create_error_response(
                message=error_message,
                error_code="INTERNAL_SERVER_ERROR",
                details=error_details,
                request_id=request_id
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )
