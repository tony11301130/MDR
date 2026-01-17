"""
Vendor Pack Template - Adapter

Implement your vendor's adapter here.
"""

from typing import Dict, Any, List
from ...core.base_adapter import BaseAdapter
from ...core.schemas import MDRAlert, MDRProcess, MDRToolResult
from .client import VendorClient

class VendorNameAdapter(BaseAdapter):
    """
    Adapter for [Vendor Name]
    """
    
    def __init__(self, tenant_id: str, config: Dict[str, Any]):
        super().__init__(tenant_id, config)
        self.client = VendorClient(
            server_url=config['server_url'],
            api_key=config['api_key'],
            verify=config.get('verify', True)
        )
    
    def normalize_alert(self, raw_data: Dict[str, Any]) -> MDRAlert:
        """
        Convert vendor alert to MDRAlert format
        """
        # TODO: Implement vendor-specific normalization
        raise NotImplementedError("normalize_alert must be implemented")
    
    def list_processes(self, hostname: str) -> List[MDRProcess]:
        """
        Get process list from endpoint
        """
        # TODO: Implement if vendor supports this
        raise NotImplementedError("list_processes not supported by this vendor")
    
    def get_host_details(self, hostname: str) -> Dict[str, Any]:
        """
        Get host information
        """
        return self.client.get_host_info(hostname)
