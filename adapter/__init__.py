"""
MDR Adapter Module

Pack-based architecture for vendor integrations.
"""

from .core.factory import AdapterFactory
from .core.pack_loader import get_pack_loader
from .core.base_adapter import BaseAdapter
from .core.schemas import MDRAlert, MDREntity, MDRProcess, MDRToolResult

__all__ = [
    'AdapterFactory',
    'get_pack_loader',
    'BaseAdapter',
    'MDRAlert',
    'MDREntity',
    'MDRProcess',
    'MDRToolResult'
]

__version__ = '2.0.0'  # Pack-based architecture
