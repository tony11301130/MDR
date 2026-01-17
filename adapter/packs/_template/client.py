"""
Vendor Pack Template - Client

Implement your vendor's API client here.
"""

import requests
from typing import Dict, Any, Optional

class VendorClient:
    """
    API Client for [Vendor Name]
    """
    
    def __init__(self, server_url: str, api_key: str, verify: bool = True):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.verify = verify
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Internal request wrapper
        """
        url = f"{self.server_url}{endpoint}"
        response = self.session.request(method, url, verify=self.verify, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def list_alerts(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch alerts from the vendor API
        """
        return self._request('GET', '/api/alerts', params={'limit': limit})
    
    def get_host_info(self, hostname: str) -> Dict[str, Any]:
        """
        Get host details
        """
        return self._request('GET', f'/api/hosts/{hostname}')
