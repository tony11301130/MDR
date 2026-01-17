import json
import os
from adapter.drivers.fidelis_adapter import FidelisAdapter
from adapter.core.schemas import EntityType

def test_deep_normalization():
    # 模擬配置
    config = {"server_url": "mock", "username": "mock", "password": "mock"}
    adapter = FidelisAdapter(tenant_id="T1", config=config)
    
    # 測試檔案
    test_file = "Fidelis-Endpoint api test/latest_alerts.json"
    if not os.path.exists(test_file):
        print("測試檔案不存在")
        return

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        alerts = data["data"]["entities"]

    # 挑選不同類型的告警測試
    # 1. 行程類 (id 49293)
    # 2. 登錄檔類 (id 49285)
    
    for raw in alerts:
        if raw["id"] in [49293, 49285]:
            normalized = adapter.normalize_alert(raw)
            print(f"\n[告警 ID: {normalized.alert_id}]")
            print(f"標題: {normalized.title}")
            print(f"時間: {normalized.timestamp}")
            print("提取實體:")
            for e in normalized.entities:
                print(f"  - {e.type}: {e.value} ({e.metadata.get('type') or e.metadata.get('name', '')})")

if __name__ == "__main__":
    test_deep_normalization()
