"""
TrendMicro Pack - Main Entry Point
"""

from .client import TrendMicroClient
from .adapter import TrendMicroAdapter

__all__ = [
    'TrendMicroClient',
    'TrendMicroAdapter'
]

__version__ = '1.0.0'
