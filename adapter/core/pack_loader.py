"""
Pack Loader - Dynamic Pack Discovery and Loading

This module provides functionality to discover and load vendor packs dynamically.
"""

import os
import json
import importlib
from typing import Dict, Any, List, Optional
from pathlib import Path

class PackLoader:
    """Dynamically loads and manages vendor packs"""
    
    def __init__(self, packs_dir: Optional[str] = None):
        if packs_dir is None:
            # Default to packs directory relative to this file
            current_dir = Path(__file__).parent.parent
            packs_dir = current_dir / "packs"
        
        self.packs_dir = Path(packs_dir)
        self._pack_cache = {}
        self._metadata_cache = {}
    
    def discover_packs(self) -> List[str]:
        """
        Discover all available packs in the packs directory.
        
        Returns:
            List of pack names
        """
        if not self.packs_dir.exists():
            return []
        
        packs = []
        for item in self.packs_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                metadata_file = item / "pack_metadata.json"
                if metadata_file.exists():
                    packs.append(item.name)
        
        return packs
    
    def load_pack_metadata(self, pack_name: str) -> Dict[str, Any]:
        """
        Load metadata for a specific pack.
        
        Args:
            pack_name: Name of the pack
            
        Returns:
            Pack metadata dictionary
        """
        if pack_name in self._metadata_cache:
            return self._metadata_cache[pack_name]
        
        metadata_file = self.packs_dir / pack_name / "pack_metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Pack metadata not found for {pack_name}")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self._metadata_cache[pack_name] = metadata
        return metadata
    
    def get_adapter_class(self, pack_name: str):
        """
        Dynamically import and return the Adapter class from a pack.
        
        Args:
            pack_name: Name of the pack (e.g., 'Fidelis', 'TrendMicro')
            
        Returns:
            Adapter class from the pack
        """
        if pack_name in self._pack_cache:
            return self._pack_cache[pack_name]
        
        try:
            # Import the pack module
            module_path = f"adapter.packs.{pack_name}"
            pack_module = importlib.import_module(module_path)
            
            # Get the adapter class (convention: {PackName}Adapter)
            adapter_class_name = f"{pack_name}Adapter"
            adapter_class = getattr(pack_module, adapter_class_name)
            
            self._pack_cache[pack_name] = adapter_class
            return adapter_class
            
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load adapter from pack '{pack_name}': {str(e)}")
    
    def list_pack_capabilities(self, pack_name: str) -> List[str]:
        """
        Get the list of capabilities provided by a pack.
        
        Args:
            pack_name: Name of the pack
            
        Returns:
            List of capability names
        """
        metadata = self.load_pack_metadata(pack_name)
        return metadata.get("capabilities", [])
    
    def validate_pack_config(self, pack_name: str, config: Dict[str, Any]) -> bool:
        """
        Validate that a config contains all required fields for a pack.
        
        Args:
            pack_name: Name of the pack
            config: Configuration dictionary
            
        Returns:
            True if valid, False otherwise
        """
        metadata = self.load_pack_metadata(pack_name)
        required_fields = metadata.get("required_config", [])
        
        for field in required_fields:
            if field not in config:
                return False
        
        return True


# Global pack loader instance
_pack_loader = None

def get_pack_loader() -> PackLoader:
    """Get the global pack loader instance"""
    global _pack_loader
    if _pack_loader is None:
        _pack_loader = PackLoader()
    return _pack_loader
