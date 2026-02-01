"""
HTTP Client Base - Async client for external APIs
"""
import httpx
from typing import Optional, Dict, Any


class BaseHTTPClient:
    """Base HTTP client with common functionality for external API calls"""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers, override in subclass for specific auth"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async GET request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async POST request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(
                url,
                json=data,
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    def get_sync(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make sync GET request (for testing or simple scripts)"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = httpx.get(
            url,
            params=params,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def post_sync(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make sync POST request (for testing or simple scripts)"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = httpx.post(
            url,
            json=data,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
