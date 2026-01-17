import os
import sys
import logging
from fidelis_endpoint_client import FidelisEndpointClient

def load_credentials(file_path):
    """
    讀取自定義格式的憑證檔案
    """
    creds = {}
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到憑證檔案: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                creds[key.strip()] = value.strip()
    return creds

def main():
    # 設定日誌
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # 憑證檔案路徑
    creds_path = os.path.join(os.path.dirname(__file__), "fidelis_endpoint_password")
    
    try:
        logger.info("正在讀取憑證資料...")
        creds = load_credentials(creds_path)
        
        server_url = creds.get("url")
        username = creds.get("account")
        password = creds.get("password")
        
        if not all([server_url, username, password]):
            logger.error("憑證資料不完整，請檢查 fidelis_endpoint_password 檔案內容")
            return

        # 初始化客戶端 (預設 verify=False 因為測試環境常使用自簽憑證)
        client = FidelisEndpointClient(
            server_url=server_url,
            username=username,
            password=password,
            verify=False 
        )

        # 1. 測試登入
        logger.info("--- 測試 1: 登入驗證 ---")
        token = client.login()
        logger.info("登入成功！")

        # 2. 測試獲取告警列表
        logger.info("--- 測試 2: 獲取告警列表並存檔 (取 10 筆) ---")
        alerts = client.list_alerts(limit=10)
        if alerts.get("success"):
            entities = alerts.get("data", {}).get("entities", [])
            logger.info(f"成功獲取 {len(entities)} 筆告警")
            
            # 存檔至地端 JSON
            alerts_file = os.path.join(os.path.dirname(__file__), "latest_alerts.json")
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=4, ensure_ascii=False)
            logger.info(f"告警資料已存至: {alerts_file}")
            
            for i, alert in enumerate(entities[:5]): # 僅顯示前 5 筆在 console
                logger.info(f"  [{i+1}] ID: {alert.get('id')}, Name: {alert.get('name')}")
        else:
            logger.error(f"獲取告警失敗: {alerts.get('error')}")

        # 3. 測試獲取端點資料 (如果有告警主機)
        logger.info("--- 測試 3: 獲取端點詳情並存檔 ---")
        if alerts.get("success") and entities:
            first_host = entities[0].get("endpointName")
            if first_host:
                logger.info(f"正在查詢主機: {first_host}")
                host_info = client.get_host_info(host_name=first_host)
                
                # 存檔至地端 JSON
                host_file = os.path.join(os.path.dirname(__file__), "host_detail.json")
                with open(host_file, 'w', encoding='utf-8') as f:
                    json.dump(host_info, f, indent=4, ensure_ascii=False)
                logger.info(f"端點詳情已存至: {host_file}")
        
        # 4. 測試連線狀態
        logger.info("--- 測試 4: 連線測試模組 ---")
        status = client.test_module()
        logger.info(f"連線狀態結果: {status}")

    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import json # 確保有引用 json
    main()
