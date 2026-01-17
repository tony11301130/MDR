"""
Skills Tools Registration - 工具註冊模組

將所有 Skills 工具註冊到 SkillsRegistry，供 AI Engine 使用。
"""

from typing import Dict, Any
from adapter.core.factory import AdapterFactory
from .registry import skills_registry
from .investigation.host_investigation import deep_investigate_host, triage_alert
from .response.isolation import isolate_endpoint, unisolate_endpoint


# ===== 輔助函數 =====

def get_adapter_for_tenant(tenant_id: str, vendor: str, config: Dict[str, Any]):
    """獲取指定租戶的 Adapter 實例"""
    return AdapterFactory.get_adapter(vendor, tenant_id, config)


# ===== 封裝工具函數（供 AI 調用）=====

def investigate_host_tool(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str):
    """
    對指定主機進行深度調查，包含行程分析與環境檢查。
    
    這是一個高階工具，會自動執行多個步驟：
    1. 獲取主機基本資訊
    2. 列出所有行程並過濾可疑項目
    3. 彙整分析結果
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    return deep_investigate_host(adapter, hostname)


def triage_alert_tool(tenant_id: str, vendor: str, config: Dict[str, Any], raw_alert: Dict[str, Any]):
    """
    對告警進行初步篩選與富化。
    
    自動執行：
    1. 標準化告警格式
    2. 提取實體（主機、IP、檔案等）
    3. 富化實體資訊
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    return triage_alert(adapter, raw_alert)


def list_endpoint_processes_tool(tenant_id: str, vendor: str, config: Dict[str, Any], hostname: str):
    """
    獲取主機目前的行程列表（已清洗與標準化）。
    
    這是一個原子工具，只執行單一動作。
    """
    adapter = get_adapter_for_tenant(tenant_id, vendor, config)
    processes = adapter.list_processes(hostname)
    return [p.dict() for p in processes]


# ===== 註冊所有工具 =====

# 調查類工具
skills_registry.register_tool(
    name="investigate_host",
    description="深度調查主機，獲取行程與配置資訊。這是一個複合式工具，會自動執行多個調查步驟並彙整結果。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string", "description": "租戶 ID"},
            "vendor": {"type": "string", "description": "廠商名稱，如 Fidelis, TrendMicro"},
            "config": {"type": "object", "description": "廠商 API 配置"},
            "hostname": {"type": "string", "description": "目標主機名稱"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=investigate_host_tool
)

skills_registry.register_tool(
    name="triage_alert",
    description="對告警進行初步篩選與富化，自動提取實體並查詢相關資訊。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string", "description": "租戶 ID"},
            "vendor": {"type": "string", "description": "廠商名稱"},
            "config": {"type": "object", "description": "廠商 API 配置"},
            "raw_alert": {"type": "object", "description": "原始告警資料"}
        },
        "required": ["tenant_id", "vendor", "config", "raw_alert"]
    },
    func=triage_alert_tool
)

skills_registry.register_tool(
    name="list_endpoint_processes",
    description="獲取主機目前的行程列表（已標準化）。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string", "description": "租戶 ID"},
            "vendor": {"type": "string", "description": "廠商名稱"},
            "config": {"type": "object", "description": "廠商 API 配置"},
            "hostname": {"type": "string", "description": "目標主機名稱"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=list_endpoint_processes_tool
)

# 處置類工具
skills_registry.register_tool(
    name="isolate_endpoint",
    description="網路隔離威脅主機，防止威脅擴散。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string", "description": "租戶 ID"},
            "vendor": {"type": "string", "description": "廠商名稱"},
            "config": {"type": "object", "description": "廠商 API 配置"},
            "hostname": {"type": "string", "description": "目標主機名稱"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=isolate_endpoint
)

skills_registry.register_tool(
    name="unisolate_endpoint",
    description="解除主機網路隔離，恢復正常連線。",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string", "description": "租戶 ID"},
            "vendor": {"type": "string", "description": "廠商名稱"},
            "config": {"type": "object", "description": "廠商 API 配置"},
            "hostname": {"type": "string", "description": "目標主機名稱"}
        },
        "required": ["tenant_id", "vendor", "config", "hostname"]
    },
    func=unisolate_endpoint
)

# Playbook 工具
from .playbook_loader import playbook_loader

def get_playbook_tool(playbook_name: str):
    """
    獲取指定調查劇本的詳細指導步驟。
    """
    content = playbook_loader.get_playbook_content(playbook_name)
    if content:
        return {"playbook_content": content}
    else:
        return {"error": f"Playbook '{playbook_name}' not found. Available playbooks: {[p['name'] for p in playbook_loader.list_playbooks()]}"}

def list_playbooks_tool():
    """列出所有可用的劇本"""
    return playbook_loader.list_playbooks()

skills_registry.register_tool(
    name="get_playbook",
    description="獲取特定劇本(Playbook)的詳細指導內容。當需要特定場景的調查指引時使用。",
    parameters={
        "type": "object",
        "properties": {
            "playbook_name": {
                "type": "string", 
                "description": "劇本名稱，例如 'detailed_host_investigation'"
            }
        },
        "required": ["playbook_name"]
    },
    func=get_playbook_tool
)

skills_registry.register_tool(
    name="list_playbooks",
    description="列出系統中所有可用的劇本(Playbooks)。",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    },
    func=list_playbooks_tool
)
