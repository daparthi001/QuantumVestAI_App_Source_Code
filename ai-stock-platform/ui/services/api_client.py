import requests
import json
import logging
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException, Timeout, ConnectionError
from core.config.settings import settings

class APIClient:
    """Client for interacting with the QuantumVestAI backend API"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the API client with optional authentication token"""
        self.base_url = settings.API_BASE_URL
        self.token = token
        self.logger = logging.getLogger(__name__)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers, including auth token if available"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        return headers
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from API response")
            if response.content:
                self.logger.error(f"Response content: {response.content[:500]}...")
            raise ValueError("Invalid JSON response from API")
        except requests.HTTPError as e:
            error_detail = "Unknown error"
            
            # Try to extract error details from response
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
                elif "message" in error_data:
                    error_detail = error_data["message"]
            except:
                if response.content:
                    error_detail = response.content.decode('utf-8')[:200]
                    
            self.logger.error(f"API request failed: {e}, Detail: {error_detail}")
            
            # Re-raise with more context
            raise RequestException(f"API request failed: {error_detail}")
            
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=(5, 30)  # (connect, read) timeouts
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise Timeout(f"Request to API timed out: {endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API GET request: {str(e)}")
            raise
            
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=(5, 30)
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise Timeout(f"Request to API timed out: {endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API POST request: {str(e)}")
            raise
            
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.put(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=(5, 30)
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise Timeout(f"Request to API timed out: {endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API PUT request: {str(e)}")
            raise
            
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.delete(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=(5, 15)
            )
            return self._handle_response(response)
        except Timeout:
            self.logger.error(f"Request to {endpoint} timed out")
            raise Timeout(f"Request to API timed out: {endpoint}")
        except ConnectionError:
            self.logger.error(f"Connection to API failed: {endpoint}")
            raise ConnectionError(f"Could not connect to API: {self.base_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error in API DELETE request: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False

    def is_premium_feature_available(self, feature_name: str) -> bool:
        """Check if a premium feature is available for the current user"""
        # If no token, premium features are not available
        if not self.token:
            return False
            
        try:
            response = self.get("/api/users/feature-access", params={"feature": feature_name})
            return response.get("available", False)
        except:
            # If the check fails, default to not available
            return False