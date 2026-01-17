from typing import Dict, Any, List
from ..core.factory import AdapterFactory
from ..core.tool_registry import tool_registry
from .investigation_skills import InvestigationSkills

def get_adapter_for_tenant(tenant_id: str, vendor: str, config: Dict[str, Any]):
    return AdapterFactory.get_adapter(vendor, tenant_id, config)

# --- 定義標準工具函數 ---

def investigate_host(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str):
    """
    對指定主機進行深度調查，包含行程分析與環境檢查。
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    return InvestigationSkills.deep_investigate_host(adapter, hostname)

def isolate_endpoint(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str):
    """
    隔離指定主機以防止威脅擴散。
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    return adapter.isolate_host(hostname).dict()

def list_endpoint_processes(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str):
    """
    獲取主機目前的行程列表（已清洗與標準化）。
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    processes = adapter.list_processes(hostname)
    return [p.dict() for p in processes]

# --- 註冊工具到註冊表，以便 AI 讀取 Schema ---

tool_registry.register_tool(
    name="investigate_host",
    description="深度調查主機，獲取行程與配置資訊。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
            "vendor": {"type": "string"},
            "config": {"type": "object"},
            "hostname": {"type": "string"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=investigate_host
)

tool_registry.register_tool(
    name="isolate_endpoint",
    description="網路隔離威脅主機。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
            "vendor": {"type": "string"},
            "config": {"type": "object"},
            "hostname": {"type": "string"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=isolate_endpoint
)
