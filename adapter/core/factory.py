from typing import Dict, Any
from .base_adapter import BaseAdapter
from .pack_loader import get_pack_loader

class AdapterFactory:
    """
    Factory for creating vendor-specific adapters using the pack system.
    """
    
    @staticmethod
    def get_adapter(vendor: str, tenant_id: str, config: Dict[str, Any]) -> BaseAdapter:
        """
        Dynamically load and instantiate an adapter from a pack.
        
        Args:
            vendor: Vendor name (e.g., 'Fidelis', 'TrendMicro')
            tenant_id: Tenant identifier
            config: Vendor-specific configuration
            
        Returns:
            Instantiated adapter instance
        """
        pack_loader = get_pack_loader()
        
        # Validate configuration
        if not pack_loader.validate_pack_config(vendor, config):
            raise ValueError(f"Invalid configuration for {vendor} pack. Check required_config in pack metadata.")
        
        # Get adapter class and instantiate
        adapter_class = pack_loader.get_adapter_class(vendor)
        return adapter_class(tenant_id=tenant_id, config=config)
    
    @staticmethod
    def list_available_vendors() -> list:
        """
        List all available vendor packs.
        
        Returns:
            List of vendor names
        """
        pack_loader = get_pack_loader()
        return pack_loader.discover_packs()
