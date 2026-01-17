import json
import os
import sys

# 將當前目錄加入 path 以便引用 adapter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adapter.drivers.fidelis_adapter import FidelisAdapter
from adapter.core.cleaner import DataCleaner

def verify_ai_optimizer():
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
    
    print(f"--- 測試開始: 驗證 AI 優化效果 ---")
    
    for i, raw_alert in enumerate(entities[:3]):
        # 未優化前的原始大小 (估算)
        original_size = len(json.dumps(raw_alert))
        
        # 執行正規化 (內含優化)
        m_alert = adapter.normalize_alert(raw_alert)
        
        # 優化後的大小
        optimized_size = len(json.dumps(m_alert.raw_data))
        reduction = (1 - (optimized_size / original_size)) * 100
        
        print(f"[{i+1}] Title: {m_alert.title}")
        print(f"    - Original Size: {original_size} chars")
        print(f"    - Optimized Size: {optimized_size} chars")
        print(f"    - Token Reduction: {reduction:.2f}%")
        
        # 顯示優化後的關鍵欄位範例
        print(f"    - Optimized Keys: {list(m_alert.raw_data.keys())}")
        if 'telemetry' in m_alert.raw_data:
             t = m_alert.raw_data['telemetry']
             if isinstance(t, dict):
                 print(f"    - Telemetry Keys: {list(t.keys())}")
        
        print("-" * 50)

if __name__ == "__main__":
    verify_ai_optimizer()
