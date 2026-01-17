"""
Host Investigation Skills - 主機調查劇本

提供主機深度調查相關的複合式劇本。
"""

from typing import Dict, Any
from adapter.core.base_adapter import BaseAdapter


def deep_investigate_host(adapter: BaseAdapter, hostname: str) -> Dict[str, Any]:
    """
    [Skill] 深度調查主機。
    這是一個複合劇本，一次執行多個動作並彙整結果，以節省 AI Token。
    
    Args:
        adapter: Adapter 實例（可以是任何廠商的 Adapter）
        hostname: 目標主機名稱
        
    Returns:
        包含主機資訊、可疑行程、告警摘要的字典
    """
    results = {
        "host_info": None,
        "suspicious_processes": [],
        "recent_alerts": [],
        "summary": ""
    }
    
    # 1. 獲取主機基本資產資訊
    results["host_info"] = adapter.get_host_details(hostname)
    
    # 2. 獲取行程清單並過濾可疑項目 (清洗邏輯在地端跑)
    all_processes = adapter.list_processes(hostname)
    # 簡單過濾邏輯：無簽章或在下載目錄執行 (這只是範例，實際會更複雜)
    for p in all_processes:
        is_suspicious = False
        if p.executable_path and "Downloads" in p.executable_path:
            is_suspicious = True
        if is_suspicious:
            results["suspicious_processes"].append(p.dict())
    
    # 3. 彙整結論 (AI 只需要看這個彙整)
    results["summary"] = f"主機 {hostname} 目前有 {len(results['suspicious_processes'])} 個可疑行程在執行中。"
    if results["suspicious_processes"]:
        results["summary"] += " 建議檢查網路連線或進行隔離。"
        
    return results


def triage_alert(adapter: BaseAdapter, raw_alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    [Skill] 告警初篩。
    自動富化告警中的主機與檔案資訊。
    
    Args:
        adapter: Adapter 實例
        raw_alert: 原始告警資料
        
    Returns:
        包含標準化告警與富化資訊的字典
    """
    normalized = adapter.normalize_alert(raw_alert)
    entities = normalized.entities
    
    enrichments = {}
    for entity in entities:
        if entity.type == "HOST":
            enrichments[entity.value] = adapter.get_host_details(entity.value)
            
    return {
        "normalized_alert": normalized.dict(),
        "enrichments": enrichments
    }
