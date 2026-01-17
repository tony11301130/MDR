from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..schemas import MDRAlert

class BaseMapper(ABC):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    @abstractmethod
    def map(self, raw_data: Dict[str, Any]) -> MDRAlert:
        """將原始資料對映到 MDRAlert 格式。"""
        pass
