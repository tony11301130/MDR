import json
import os
from adapter.core.factory import AdapterFactory
from skills.investigation.host_investigation import deep_investigate_host

def verify_flow():
    # 1. 模擬租戶配置 (Tenant Config)
    tenant_config = {
        "vendor": "fidelis",
        "tenant_id": "T-CUSTOMER-A",
        "config": {
            "server_url": "https://127.0.0.1",
            "username": "admin",
            "password": "password",
            "verify": False
        }
    }
    
    # 2. 獲取轉接器
    adapter = AdapterFactory.get_adapter(
        vendor=tenant_config["vendor"],
        tenant_id=tenant_config["tenant_id"],
        config=tenant_config["config"]
    )
    
    print(f"--- 轉接器已啟動: {type(adapter).__name__} ---")
    
    # 3. 讀取測試資料
    alert_file = "Fidelis-Endpoint api test/latest_alerts.json"
    if not os.path.exists(alert_file):
        print(f"找不到測試檔案: {alert_file}")
        return
        
    with open(alert_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    # 取第一筆測試告警
    raw_alert = raw_data["data"]["entities"][1] # 第二筆 wacs.exe
    
    # 4. 階段一：資料清洗 (Normalization)
    normalized = adapter.normalize_alert(raw_alert)
    print("\n[階段一：資料清洗結果]")
    print(f"標題: {normalized.title}")
    print(f"嚴重程度: {normalized.severity}")
    print(f"提取實體: {[e.value for e in normalized.entities]}")
    
    print(f"\n[資料清洗檢查]")
    print(f"原始資料對象數: {len(raw_alert.keys())}")
    print(f"清洗後對象數: {len(normalized.raw_data.keys())}")
    print(f"原始 Key: {list(raw_alert.keys())[:5]}...")
    print(f"清洗後 Key: {list(normalized.raw_data.keys())[:5]}...")
    
    # 檢查是否有排除 'links'
    if 'links' in normalized.raw_data:
        print("警告: 清洗失敗，冗餘欄位 'links' 依然存在")
    else:
        print("成功: 冗餘欄位 'links' 已被移除")
    
    # 5. 階段二：劇本執行 (Skill execution)
    # 這裡我們模擬主機調查，因為沒真的連線，我們假設 list_processes 已被 Mock
    print("\n[階段二：執行 Skill - DeepInvestigateHost]")
    # 為了測試，我們 Monkeypatch 一下 list_processes
    from adapter.core.schemas import MDRProcess
    adapter.list_processes = lambda hostname: [
        MDRProcess(pid=6936, name="wacs.exe", executable_path="C:\\Users\\Administrator\\Downloads\\wacs.exe")
    ]
    adapter.get_host_details = lambda hostname: {"OS": "Windows 10", "Domain": "SIMPRO"}
    
    skill_result = deep_investigate_host(adapter, "WIN-8F6DDKRJ75B")
    
    print(f"總結: {skill_result['summary']}")
    print(f"可疑行程數: {len(skill_result['suspicious_processes'])}")
    
    print("\n--- 驗證流程結束 ---")

if __name__ == "__main__":
    verify_flow()
