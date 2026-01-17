import requests
import json
import logging
import urllib3
from typing import Dict, List, Any, Optional

# 關閉自簽憑證產生的警告資訊
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FidelisEndpointClient:
    """
    Fidelis Endpoint API 獨立客戶端。
    """
    
    def __init__(self, server_url: str, username: str, password: str, verify: bool = False, proxy: Optional[str] = None):
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

    def _http_request(self, method: str, url_suffix: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, resp_type: str = "json") -> Any:
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
            response.raise_for_status()
            if resp_type == "json":
                return response.json()
            else:
                return response.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API 請求失敗: {method} {url}, 錯誤: {str(e)}")
            raise e

    def login(self) -> str:
        params = {"username": self.username, "password": self.password}
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
            raise Exception(f"登入失敗: {data.get('error', '未知錯誤')}")
        self.token = data.get("data", {}).get("token")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        return self.token

    def test_module(self) -> str:
        try:
            self.list_alerts(limit=1)
            return "ok"
        except Exception as e:
            return f"測試失敗: {str(e)}"

    def list_alerts(self, limit: int = 50, sort: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        url_suffix = "/alerts/getalertsV2"
        params = {"take": limit}
        if sort: params["sort"] = sort
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        return self._http_request("GET", url_suffix, params=params)

    def get_host_info(self, host_name: Optional[str] = None, ip_address: Optional[str] = None) -> Dict:
        url_suffix = "/endpoints/v2/0/100/hostname Ascending"
        field_name = "HostName" if host_name else "IpAddress"
        value = host_name or ip_address
        if not value:
            raise ValueError("必須提供 host_name 或 ip_address")

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

    def query_events(self, entity_type: str, column: str, value: str, operator: str = "=", logic: str = "AND", limit: int = 500) -> Dict:
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
