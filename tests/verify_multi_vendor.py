import json
from adapter.core.factory import AdapterFactory

def verify_multi_vendor():
    # 1. 模擬不同廠牌的原始資料
    fidelis_raw = {
        "id": 1001,
        "name": "Malicious Process Detected",
        "severity": 4,
        "endpointName": "PC-01",
        "ipAddress": "192.168.1.10",
        "links": {"self": "http://api/1001"} # 冗餘資料
    }
    
    trend_raw = {
        "id": "WB-XYZ",
        "description": "Vision One Threat Found",
        "severity": "critical",
        "entities": [
            {"entityType": "host", "entityValue": "PC-02"},
            {"entityType": "ip", "entityValue": "10.0.0.5"}
        ],
        "metadata_version": "1.0", # 冗餘資料
        "extra_info": None # 空值
    }

    # 2. 定義租戶配置
    tenants = {
        "T-FIDELIS": {"vendor": "fidelis", "config": {"server_url": "s1", "username": "u1", "password": "p1"}},
        "T-TREND": {"vendor": "trendmicro", "config": {"api_url": "v1", "api_key": "k1"}}
    }

    # 3. 執行標準化與清洗
    for t_id, t_info in tenants.items():
        adapter = AdapterFactory.get_adapter(t_info["vendor"], t_id, t_info["config"])
        
        raw_data = fidelis_raw if t_info["vendor"] == "fidelis" else trend_raw
        normalized = adapter.normalize_alert(raw_data)
        
        print(f"\n[租戶: {t_id}]")
        print(f"廠商: {normalized.vendor}")
        print(f"標準化標題: {normalized.title}")
        print(f"標準化嚴重程度: {normalized.severity}")
        print(f"提取實體: {[e.value for e in normalized.entities]}")
        print(f"清洗後原始欄位: {list(normalized.raw_data.keys())}")
        
        # 驗證清洗效果
        if "links" in normalized.raw_data or "metadata_version" in normalized.raw_data:
            print("[X] 清洗失敗：發現冗餘欄位")
        else:
            print("[V] 清洗成功：冗餘欄位已移除")

if __name__ == "__main__":
    verify_multi_vendor()
