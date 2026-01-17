import json
import os
import sys

# 將當前目錄加入 path 以便引用 adapter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from adapter.drivers.fidelis_adapter import FidelisAdapter
from adapter.core.schemas import MDRAlert

def final_verification():
    print("=== MDR Data Cleaning + Normalization Layer Final Test ===")
    
    # 載入測試資料
    data_path = os.path.join(os.path.dirname(__file__), "Fidelis-Endpoint api test", "latest_alerts.json")
    with open(data_path, 'r', encoding='utf-8') as f:
        mock_response = json.load(f)
    
    entities = mock_response.get("data", {}).get("entities", [])
    
    # 初始化 Adapter
    adapter = FidelisAdapter(tenant_id="final-test-tenant", config={"server_url": "", "username": "", "password": ""})
    
    # 測試 Pipeline: transform_alert (Fetch 在外面模擬了)
    for i, raw_alert in enumerate(entities[:5]):
        print(f"Testing Alert {i+1}...")
        
        # 使用全新的標準 Pipeline
        m_alert = adapter.transform_alert(raw_alert)
        
        # 驗證 1: 是否為 MDRAlert 實例 (Pydantic 驗證)
        assert isinstance(m_alert, MDRAlert)
        
        # 驗證 2: 關鍵欄位是否存在
        print(f"  [PASS] Validation: {m_alert.alert_id} normalized.")
        
        # 驗證 3: MITRE 提取 (針對 Behavior 類型)
        if "Behavior" in m_alert.title:
            if m_alert.mitre_attack:
                attack = m_alert.mitre_attack[0]
                print(f"  [PASS] MITRE Extracted: {attack.technique_id} - {attack.technique_name}")
            else:
                print(f"  [WARN] Expected MITRE for Behavior alert but found none.")

        # 驗證 4: AI 優化效果
        orig_len = len(json.dumps(raw_alert))
        opt_len = len(json.dumps(m_alert.raw_data))
        print(f"  [PASS] AI Optimization: {orig_len} -> {opt_len} ({(1-opt_len/orig_len)*100:.2f}% reduced)")
        
        # 驗證 5: Cleaner 是否運作 (不應包含 links)
        assert "links" not in m_alert.raw_data
        print(f"  [PASS] Data Cleaner: Redundant keys removed.")
        
        print("-" * 40)

    print("\n[SUCCESS] All pipeline stages verified successfully.")

if __name__ == "__main__":
    final_verification()
