"""
QuantumVestAI API Client
Last Updated: 2025-06-18 21:25:2
Author: daparthi001
"""
import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
# Attempt to load settings from the shared core package first.  In some
# testing environments the ``ui`` package inserts its own ``core`` package
# ahead of the shared one which lacks ``get_settings``.  If that happens,
# explicitly prepend the project root so the correct package is found.
try:
    from core.config import get_settings  # type: ignore[attr-defined]
    if not callable(get_settings):
        raise ImportError
except (ModuleNotFoundError, ImportError):
    import sys
    from pathlib import Path

    # Remove any previously imported ``core.config`` module that may have
    # originated from ``ui.core`` so we can re-import it from the project root.
    sys.modules.pop("core.config", None)

    candidate = Path(__file__).resolve()
    project_root = None
    # Walk upwards until we find a directory containing the real project
    # packages.  In Docker or testing environments ``core.config`` may resolve
    # to ``ui.core.config`` which lacks ``get_settings``.  Look for the
    # "ai-stock-platform" package (which houses ``api`` and ``core``) first and
    # fall back to any parent with a ``core/config`` directory.
    for parent in candidate.parents:
        if (parent / "ai-stock-platform" / "core" / "config").exists():
            project_root = parent / "ai-stock-platform"
            break
        if (parent / "core" / "config").exists() and project_root is None:
            project_root = parent
    if project_root and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from core.config import get_settings  # type: ignore[attr-defined]
        if not callable(get_settings):
            raise ImportError
    except (ModuleNotFoundError, ImportError) as e:
        try:
            from api.core.config.settings import get_settings
        except ModuleNotFoundError as e2:  # pragma: no cover - environment issue
            raise ImportError(
                "Could not import settings from either 'core.config' or 'api.core.config.settings'. "
                "Make sure PYTHONPATH includes the project directory."
            ) from e2
from requests.exceptions import ConnectionError, RequestException, Timeout


class APIClient:
    """Client for interacting with the QuantumVestAI backend API"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the API client with optional authentication token"""
        self.base_url = get_settings().API_BASE_URL
        self.token = token
        self.timeout = 10  # Default timeout in seconds
        self.logger = logging.getLogger(__name__)
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers, including auth token if available"""
        return self._get_headers()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers, including auth token if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        return headers
    
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Ensure endpoint has the correct /api/v1 prefix"""
        # If endpoint already starts with /api/v1, leave it as is
        if endpoint.startswith("/api/v1"):
            return endpoint
            
        # If endpoint starts with /, append it to /api/v1
        if endpoint.startswith("/"):
            return f"/api/v1{endpoint}"
            
        # If endpoint doesn't start with /, add /api/v1/
        return f"/api/v1/{endpoint}"
    
    def build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint, handling base paths gracefully."""
        normalized = self._normalize_endpoint(endpoint)
        base = self.base_url.rstrip("/")
        return urljoin(base, normalized)
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except ValueError:
            self.logger.error("Failed to decode JSON from API response")
            if response.content:
                self.logger.error(f"Response content: {response.content[:500]}...")
            raise ValueError("Invalid JSON response from API")
        except requests.HTTPError as e:
            error_detail = "Unknown error"
            
            # Try to extract error details from response
            try:
                if response.content:
                    error_detail = response.content.decode('utf-8')[:200]
            except:
                pass
                    
            self.logger.error(f"API request failed: {e}, Detail: {error_detail}")
            
            # Re-raise with more context
            raise RequestException(f"API request failed: {error_detail}")
            
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API"""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        url = self.build_url(endpoint)
        
        self.logger.debug(f"Making GET request to {url}")
        try:
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {normalized_endpoint} timed out")
            raise Timeout(f"Request to API timed out: {normalized_endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {normalized_endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API GET request: {str(e)}")
            raise
            
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the API"""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        url = self.build_url(endpoint)

        self.logger.debug(f"Making POST request to {url}")
        try:
            response = requests.post(
                url,
                data=json.dumps(data) if data else None,
                headers=self._get_headers(),
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {normalized_endpoint} timed out")
            raise Timeout(f"Request to API timed out: {normalized_endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {normalized_endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API POST request: {str(e)}")
            raise

    def post_form(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request with form-encoded data."""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        url = self.build_url(endpoint)

        headers = self._get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        self.logger.debug(f"Making FORM POST request to {url}")
        try:
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {normalized_endpoint} timed out")
            raise Timeout(f"Request to API timed out: {normalized_endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {normalized_endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API POST request: {str(e)}")
            raise
            
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request to the API"""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        url = self.build_url(endpoint)
        
        self.logger.debug(f"Making PUT request to {url}")
        try:
            response = requests.put(url, data=json.dumps(data) if data else None, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {normalized_endpoint} timed out")
            raise Timeout(f"Request to API timed out: {normalized_endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {normalized_endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API PUT request: {str(e)}")
            raise
            
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request to the API"""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        url = self.build_url(endpoint)
        
        self.logger.debug(f"Making DELETE request to {url}")
        try:
            # Only include params if they are provided
            kwargs = {'headers': self._get_headers(), 'timeout': self.timeout}
            if params:
                kwargs['params'] = params
            response = requests.delete(url, **kwargs)
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {normalized_endpoint} timed out")
            raise Timeout(f"Request to API timed out: {normalized_endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {normalized_endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API DELETE request: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = self.get("/health")
            return response.get("status") == "healthy"
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def is_premium_feature_available(self, feature_name: str) -> bool:
        """Check if a premium feature is available for the current user"""
        # If no token, premium features are not available
        if not self.token:
            return False
            
        try:
            response = self.get(f"/features/{feature_name}")
            return response.get("available", False)
        except Exception as e:
            self.logger.error(f"Failed to check premium feature availability: {str(e)}")
            # If the check fails, default to not available
            return False
    
    def enable_advanced_features(self) -> Dict[str, Any]:
        """Enable advanced features for the current user"""
        try:
            response = self.post("/features/enable-advanced")
            return response
        except Exception as e:
            self.logger.error(f"Failed to enable advanced features: {str(e)}")
            raise

    def get_available_features(self) -> Dict[str, Any]:
        """Get all available features for the current user"""
        try:
            response = self.get("/features")
            return response
        except Exception as e:
            self.logger.error(f"Failed to get available features: {str(e)}")
            return {"features": {}}
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return auth data"""
        try:
            auth_data = {
                "username": username,
                "password": password
            }
            response = self.post_form("/auth/login", data=auth_data)
            return response
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return None
