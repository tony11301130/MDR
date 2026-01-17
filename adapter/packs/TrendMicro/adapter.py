import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.base_adapter import BaseAdapter
from ..core.schemas import MDRAlert, Severity, MDREntity, EntityType, MDRToolResult, MDRProcess
from ..core.cleaner import DataCleaner
from .trendmicro_client import TrendMicroVisionOneClient

class TrendMicroAdapter(BaseAdapter):
    """
    Trend Micro Vision One 轉接器
    包含 API Playbook 層與資料清洗與正規化層的實作。
    """
    def __init__(self, tenant_id: str, config: Dict[str, Any]):
        super().__init__(tenant_id, config)
        self.client = TrendMicroVisionOneClient(
            api_url=config["api_url"],
            api_key=config["api_key"],
            verify=config.get("verify", True)
        )

    def _map_severity(self, vendor_severity: str) -> Severity:
        mapping = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO
        }
        return mapping.get(vendor_severity.lower(), Severity.INFO)

    def normalize_alert(self, raw_data: Dict[str, Any]) -> MDRAlert:
        """
        [正規化層] 轉化 Trend Micro 原始告警為 MDRAlert
        """
        entities = []
        
        # Trend Micro 告警結構通常在 entities 欄位
        vendor_entities = raw_data.get("entities", [])
        for ent in vendor_entities:
            ent_type = ent.get("entityType")
            ent_value = ent.get("entityValue")
            
            if ent_type == "host":
                entities.append(MDREntity(type=EntityType.HOST, value=ent_value))
            elif ent_type == "ip":
                entities.append(MDREntity(type=EntityType.IP, value=ent_value))
            elif ent_type == "file":
                entities.append(MDREntity(type=EntityType.FILE, value=ent_value))
            elif ent_type == "user":
                entities.append(MDREntity(type=EntityType.USER, value=ent_value))

        return MDRAlert(
            alert_id=raw_data.get("id", "unknown"),
            vendor="Trend Micro Vision One",
            tenant_id=self.tenant_id,
            timestamp=raw_data.get("createdTime") or datetime.now(),
            severity=self._map_severity(raw_data.get("severity", "medium")),
            title=raw_data.get("description", "Vision One Alert"),
            entities=entities,
            raw_data=raw_data # raw_data will be cleaned by transform_alert
        )


    def list_processes(self, hostname: str) -> List[MDRProcess]:
        """
        [API Playbook 層] 封裝複雜的查詢邏輯
        """
        # 第一步：獲取 Endpoint ID (Vision One 查詢通常需要 GUID)
        search_res = self.client.search_endpoints(f"endpointName eq '{hostname}'")
        endpoints = search_res.get("items", [])
        if not endpoints:
            return []
        
        endpoint_id = endpoints[0].get("agentGuid")
        
        # 第二步：獲取行程遙測資料
        raw_telemetry = self.client.get_edr_telemetry(endpoint_id, "process_list")
        
        # 第三步：[清洗與正規化]
        processes = []
        for p in raw_telemetry.get("data", []):
            processes.append(MDRProcess(
                pid=p.get("processId"),
                ppid=p.get("parentProcessId"),
                name=p.get("processName"),
                command_line=p.get("commandLine"),
                executable_path=p.get("imagePath"),
                username=p.get("user")
            ))
        return processes

    def isolate_host(self, hostname: str) -> MDRToolResult:
        start_time = time.time()
        # [API Playbook] 封裝隔離邏輯
        try:
            search_res = self.client.search_endpoints(f"endpointName eq '{hostname}'")
            endpoint_id = search_res.get("items", [{}])[0].get("agentGuid")
            
            if not endpoint_id:
                return MDRToolResult(status="error", data=None, message="Host not found", execution_time=time.time()-start_time)
            
            res = self.client.run_command(endpoint_id, "isolate", {})
            return MDRToolResult(status="success", data=res, message="Isolation triggered", execution_time=time.time()-start_time)
        except Exception as e:
            return MDRToolResult(status="error", data=None, message=str(e), execution_time=time.time()-start_time)

    def terminate_process(self, hostname: str, pid: int) -> MDRToolResult:
        """
        [API Playbook] 終止惡意程序
        """
        start_time = time.time()
        try:
            search_res = self.client.search_endpoints(f"endpointName eq '{hostname}'")
            endpoints = search_res.get("items", [])
            if not endpoints:
                return MDRToolResult(status="error", data=None, message="Host not found", execution_time=time.time()-start_time)
            
            endpoint_id = endpoints[0].get("agentGuid")
            
            # 執行終止程序指令
            res = self.client.run_command(endpoint_id, "terminate_process", {"pid": pid})
            return MDRToolResult(
                status="success", 
                data=res, 
                message=f"Process {pid} termination triggered on {hostname}", 
                execution_time=time.time()-start_time
            )
        except Exception as e:
            return MDRToolResult(status="error", data=None, message=str(e), execution_time=time.time()-start_time)

    def get_host_details(self, hostname: str) -> Dict[str, Any]:
        search_res = self.client.search_endpoints(f"endpointName eq '{hostname}'")
        return search_res.get("items", [{}])[0]
