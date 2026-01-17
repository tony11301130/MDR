import json
import os
import sys

# 將當前目錄加入 path 以便引用 adapter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adapter.drivers.fidelis_adapter import FidelisAdapter
from adapter.core.schemas import MDRAlert

def verify_mapper():
    # 載入測試資料
    data_path = os.path.join(os.path.dirname(__file__), "Fidelis-Endpoint api test", "latest_alerts.json")
    with open(data_path, 'r', encoding='utf-8') as f:
        mock_response = json.load(f)
    
    entities = mock_response.get("data", {}).get("entities", [])
    if not entities:
        print("Error: No entities found in latest_alerts.json")
        return

    # 初始化 Adapter
    adapter = FidelisAdapter(tenant_id="test-tenant", config={"server_url": "", "username": "", "password": ""})
    
    print(f"--- 測試開始: 轉換 {len(entities)} 筆告警 ---")
    
    for i, raw_alert in enumerate(entities[:10]):
        try:
            m_alert = adapter.normalize_alert(raw_alert)
            print(f"[{i+1}] ID: {m_alert.alert_id} | Severity: {m_alert.severity} | Title: {m_alert.title}")
            
            # 驗證 MITRE 提取
            if m_alert.mitre_attack:
                for attack in m_alert.mitre_attack:
                    print(f"    -> MITRE: {attack.technique_id} ({attack.technique_name})")
            
            # 驗證實體
            if m_alert.entities:
                for entity in m_alert.entities:
                    print(f"    -> Entity: {entity.type} = {entity.value}")
                    
            print("-" * 30)
        except Exception as e:
            print(f"Error processing alert {i}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_mapper()
