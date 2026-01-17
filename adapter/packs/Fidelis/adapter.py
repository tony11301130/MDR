import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...core.base_adapter import BaseAdapter
from ...core.schemas import MDRAlert, Severity, MDREntity, EntityType, MDRToolResult, MDRProcess
from ...core.cleaner import DataCleaner
from .client import FidelisEndpointClient

class FidelisAdapter(BaseAdapter):
    def __init__(self, tenant_id: str, config: Dict[str, Any]):
        super().__init__(tenant_id, config)
        self.client = FidelisEndpointClient(
            server_url=config["server_url"],
            username=config["username"],
            password=config["password"],
            verify=config.get("verify", False),
            proxy=config.get("proxy")
        )

    def _map_severity(self, vendor_severity: int) -> Severity:
        mapping = {
            5: Severity.CRITICAL,
            4: Severity.HIGH,
            3: Severity.MEDIUM,
            2: Severity.LOW,
            1: Severity.INFO
        }
        return mapping.get(vendor_severity, Severity.INFO)

    def normalize_alert(self, raw_data: Dict[str, Any]) -> MDRAlert:
        from .mapper import FidelisMapper
        mapper = FidelisMapper(self.tenant_id)
        return mapper.map(raw_data)

    def transform_alert(self, raw_data: Dict[str, Any], event_type: str = None) -> MDRAlert:
        if event_type is None:
            from .mapper import FidelisMapper
            event_type = FidelisMapper(self.tenant_id).get_event_type(raw_data)
        return super().transform_alert(raw_data, event_type=event_type)

    def list_processes(self, hostname: str) -> List[MDRProcess]:
        # 透過 query_events 獲取最近的行程事件
        # EntityType 0 = Process in Fidelis V2 Events API (通常)
        # 這裡簡化為查詢該主機的所有 Process 事件
        raw_response = self.client.query_events(
            entity_type="Process",
            column="EndpointName",
            operator="=",
            value=hostname,
            limit=100
        )
        
        # 這裡體現「清洗層」：過濾掉非必要的事件資料
        events = raw_response.get("data", [])
        
        processes = []
        seen_pids = set()
        
        for event in events:
            # 清洗並優化 event 資料以提取有效資訊
            telemetry_str = event.get("telemetry")
            if not telemetry_str: continue
            
            try:
                t = json.loads(telemetry_str)
                pid = t.get("PID")
                if pid and pid not in seen_pids:
                    processes.append(MDRProcess(
                        pid=pid,
                        ppid=t.get("PPID"),
                        name=t.get("Name"),
                        command_line=t.get("CommandLine"),
                        executable_path=t.get("Path"),
                        username=t.get("User"),
                        hash={"sha256": t.get("HashSHA256"), "md5": t.get("HashMD5")} if t.get("HashMD5") else None
                    ))
                    seen_pids.add(pid)
            except:
                continue
                
        return processes

    def isolate_host(self, hostname: str) -> MDRToolResult:
        start_time = time.time()
        try:
            # 從設定中獲取隔離腳本 ID
            script_id = self.config.get("fidelis_isolate_script_id")
            if not script_id:
                return MDRToolResult(status="error", data=None, message="Missing 'fidelis_isolate_script_id' in config", execution_time=time.time() - start_time)
            
            # 首先獲取主機 IP
            host_info = self.client.get_host_info(host_name=hostname)
            entities = host_info.get("data", {}).get("entities", [])
            if not entities:
                return MDRToolResult(status="error", data=None, message=f"Host '{hostname}' not found", execution_time=time.time() - start_time)
            
            ip = entities[0].get("ipAddress")
            if not ip:
                return MDRToolResult(status="error", data=None, message=f"Could not find IP for host '{hostname}'", execution_time=time.time() - start_time)
            
            # 執行隔離腳本
            job_id = self.client.execute_script(script_id=script_id, endpoint_ip=ip)
            
            return MDRToolResult(
                status="success", 
                data={"hostname": hostname, "ip": ip, "job_id": job_id}, 
                message=f"Isolation job '{job_id}' triggered for {hostname}", 
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return MDRToolResult(status="error", data=None, message=str(e), execution_time=time.time() - start_time)

    def terminate_process(self, hostname: str, pid: int) -> MDRToolResult:
        start_time = time.time()
        try:
            # 從設定中獲取終止程序腳本 ID
            script_id = self.config.get("fidelis_terminate_process_script_id")
            if not script_id:
                return MDRToolResult(status="error", data=None, message="Missing 'fidelis_terminate_process_script_id' in config", execution_time=time.time() - start_time)
            
            # 獲取主機 IP
            host_info = self.client.get_host_info(host_name=hostname)
            entities = host_info.get("data", {}).get("entities", [])
            if not entities:
                 return MDRToolResult(status="error", data=None, message=f"Host '{hostname}' not found", execution_time=time.time() - start_time)
            
            ip = entities[0].get("ipAddress")
            
            # 執行終止程序腳本 (通常需要 PID 作為回答/參數)
            job_id = self.client.execute_script(script_id=script_id, endpoint_ip=ip, answer=str(pid))
            
            return MDRToolResult(
                status="success", 
                data={"pid": pid, "hostname": hostname, "job_id": job_id}, 
                message=f"Termination job '{job_id}' triggered for PID {pid} on {hostname}", 
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return MDRToolResult(status="error", data=None, message=str(e), execution_time=time.time() - start_time)

    def get_host_details(self, hostname: str) -> Dict[str, Any]:
        response = self.client.get_host_info(host_name=hostname)
        return response.get("data", {}).get("entities", [{}])[0]
