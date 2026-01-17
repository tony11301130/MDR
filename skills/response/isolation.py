"""
Isolation Skills - 隔離處置劇本

提供主機隔離與解除隔離相關的處置動作。
"""

from typing import Dict, Any
from adapter.core.factory import AdapterFactory


def isolate_endpoint(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str) -> Dict[str, Any]:
    """
    隔離指定主機以防止威脅擴散。
    
    Args:
        tenant_id: 租戶 ID
        vendor: 廠商名稱（如 "Fidelis", "TrendMicro"）
        config: 廠商配置（包含 API 認證資訊）
        hostname: 目標主機名稱
        
    Returns:
        隔離操作的執行結果
    """
    adapter = AdapterFactory.get_adapter(vendor, tenant_id, config)
    result = adapter.isolate_host(hostname)
    return result.dict()


def unisolate_endpoint(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str) -> Dict[str, Any]:
    """
    解除主機隔離，恢復網路連線。
    
    Args:
        tenant_id: 租戶 ID
        vendor: 廠商名稱
        config: 廠商配置
        hostname: 目標主機名稱
        
    Returns:
        解除隔離操作的執行結果
    """
    adapter = AdapterFactory.get_adapter(vendor, tenant_id, config)
    # 注意：這裡假設 BaseAdapter 有 unisolate_host 方法
    # 如果沒有，需要先在 BaseAdapter 中定義
    if hasattr(adapter, 'unisolate_host'):
        result = adapter.unisolate_host(hostname)
        return result.dict()
    else:
        return {
            "success": False,
            "message": f"Vendor {vendor} does not support unisolate operation"
        }
