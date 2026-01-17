from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .schemas import MDRAlert, MDRProcess, MDRToolResult

class BaseAdapter(ABC):
    def __init__(self, tenant_id: str, config: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.config = config

    @abstractmethod
    def normalize_alert(self, raw_data: Dict[str, Any]) -> MDRAlert:
        """將廠商原始告警資料轉換為標準 MDRAlert 格式。"""
        pass

    def transform_alert(self, raw_data: Dict[str, Any], event_type: str = "generic") -> MDRAlert:
        """
        標準化處理管道：Clean -> Map -> Optimize -> Validate
        """
        from .cleaner import DataCleaner
        
        # 1. 基礎清理 (移除空值與冗餘)
        clean_raw = DataCleaner.clean_dict(raw_data)
        
        # 2. 正規化對映 (由子類實作)
        alert = self.normalize_alert(clean_raw)
        
        # 3. AI Token 優化
        alert.raw_data = DataCleaner.optimize_for_ai(alert.raw_data, event_type=event_type)
        
        # 4. 驗證 (Pydantic 自動處理，這裡可以加額外的邏輯)
        return alert


    @abstractmethod
    def list_processes(self, hostname: str) -> List[MDRProcess]:
        """獲取指定主機的執行程序列表。"""
        pass

    @abstractmethod
    def isolate_host(self, hostname: str) -> MDRToolResult:
        """執行網路隔離。"""
        pass

    @abstractmethod
    def terminate_process(self, hostname: str, pid: int) -> MDRToolResult:
        """終止惡意程序。"""
        pass

    @abstractmethod
    def get_host_details(self, hostname: str) -> Dict[str, Any]:
        """獲取主機詳細資訊。"""
        pass
