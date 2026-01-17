import requests
import json
import logging
import urllib3
from typing import Dict, List, Any, Optional

# 關閉自簽憑證產生的警告資訊
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FidelisEndpointClient:
    """
    Fidelis Endpoint API 獨立客戶端，用於從 XSOAR 邏輯抽離後的測試與開發。
    """
    
    def __init__(self, server_url: str, username: str, password: str, verify: bool = False, proxy: Optional[str] = None):
        """
        初始化客戶端
        
        :param server_url: Fidelis 伺服器網址 (包含 /Endpoint/api)
        :param username: 使用者帳號
        :param password: 密碼
        :param verify: 是否驗證 SSL 憑證
        :param proxy: Proxy 設定 (可選)
        """
        self.server_url = server_url.rstrip('/')
        if not self.server_url.endswith('/Endpoint/api'):
            self.server_url += '/Endpoint/api'
            
        self.username = username
        self.password = password
        self.verify = verify
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.token = None
        self.headers = {}
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _http_request(self, method: str, url_suffix: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, resp_type: str = "json") -> Any:
        """
        內部的 HTTP 請求包裝
        """
        if not self.token and url_suffix != "/authenticate":
            self.login()
            
        url = self.server_url + url_suffix
        
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=json_data,
                verify=self.verify,
                proxies=self.proxies,
                timeout=30
            )
            
            # 檢查 HTTP 錯誤
            response.raise_for_status()
            
            if resp_type == "json":
                return response.json()
            else:
                return response.content
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API 請求失敗: {method} {url}, 錯誤: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"回應內容: {e.response.text}")
            raise e

    def login(self) -> str:
        """
        執行登入並獲取 Bearer Token
        """
        self.logger.info(f"正在嘗試登入 Fidelis: {self.username}")
        params = {"username": self.username, "password": self.password}
        
        # 登入不需要目前的 headers 或 token
        temp_headers = {"Accept": "application/json"}
        
        response = requests.get(
            f"{self.server_url}/authenticate",
            params=params,
            verify=self.verify,
            headers=temp_headers,
            proxies=self.proxies,
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            error_msg = data.get("error", "未知錯誤")
            raise Exception(f"登入失敗: {error_msg}")
            
        self.token = data.get("data", {}).get("token")
        if not self.token:
            raise Exception("登入成功但未取得 Token")
            
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        self.logger.info("登入成功，已獲取 Token")
        return self.token

    def test_module(self) -> str:
        """
        測試連線與認證是否正常
        """
        try:
            self.list_alerts(limit=1)
            return "ok"
        except Exception as e:
            return f"測試失敗: {str(e)}"

    def list_alerts(self, limit: int = 50, sort: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """
        獲取告警列表
        
        :param limit: 獲取數量
        :param sort: 排序方式
        :param start_date: 開始日期 (ISO 格式)
        :param end_date: 結束日期 (ISO 格式)
        """
        url_suffix = "/alerts/getalertsV2"
        params = {
            "take": limit
        }
        if sort: params["sort"] = sort
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        
        return self._http_request("GET", url_suffix, params=params)

    def get_host_info(self, host_name: Optional[str] = None, ip_address: Optional[str] = None) -> Dict:
        """
        獲取主機細節資訊
        """
        url_suffix = "/endpoints/v2/0/100/hostname Ascending"
        
        field_name = ""
        value = ""
        
        if host_name:
            field_name = "HostName"
            value = host_name
        elif ip_address:
            field_name = "IpAddress"
            value = ip_address
        else:
            raise ValueError("必須提供 host_name 或 ip_address 其中之一")

        params = {
            "accessType": "3",
            "search": json.dumps({
                "searchFields": [{
                    "fieldName": field_name, 
                    "values": [{"value": value}]
                }]
            }),
        }

        return self._http_request("GET", url_suffix, params=params)

    def execute_script(self, script_id: str, endpoint_ip: str, answer: str = "", timeout: Optional[int] = None) -> str:
        """
        在指定端點執行腳本
        """
        url_suffix = "/jobs/createTask"
        body = {
            "timeoutInSeconds": timeout,
            "packageId": script_id,
            "endpoints": endpoint_ip,
            "isPlaybook": False,
            "taskOptions": [
                {
                    "scriptId": script_id,
                    "questions": [
                        {"paramNumber": 1, "answer": answer}
                    ],
                }
            ],
        }

        response = self._http_request("POST", url_suffix, json_data=body)
        return response.get("data") # 回傳 Job ID

    def query_events(self, entity_type: str, column: str, value: str, operator: str = "=", logic: str = "AND", limit: int = 50) -> Dict:
        """
        查詢事件 (EDR 獵捕功能)
        """
        url_suffix = "/v2/events"
        params = {"pageSize": limit}
        
        body = {
            "criteriaV3": {
                "entityType": entity_type,
                "filter": {
                    "filterType": "composite",
                    "logic": logic,
                    "filters": [{"filterType": "criteria", "column": column, "operator": operator, "value": value}],
                },
            },
        }
        
        return self._http_request("POST", url_suffix, params=params, json_data=body)
