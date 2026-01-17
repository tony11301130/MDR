import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from ...core.mappers.base_mapper import BaseMapper
from ...core.schemas import MDRAlert, Severity, MDREntity, EntityType, MitreAttack

class FidelisMapper(BaseMapper):
    def get_event_type(self, raw_data: Dict[str, Any]) -> str:
        vendor_event_type = raw_data.get("eventType")
        event_type_map = {
            0: "process",
            5: "file",
            10: "registry"
        }
        return event_type_map.get(vendor_event_type, "generic")

    def _map_severity(self, vendor_severity: int) -> Severity:
        mapping = {
            5: Severity.CRITICAL,
            4: Severity.HIGH,
            3: Severity.MEDIUM,
            2: Severity.LOW,
            1: Severity.INFO
        }
        return mapping.get(vendor_severity, Severity.INFO)

    def _parse_mitre(self, description: str, enrichments: List[str]) -> List[MitreAttack]:
        attacks = []
        
        # 從 description 提取 (MITRE ATT&CK - TA0011,T1071)
        match = re.search(r"\(MITRE ATT&CK - ([^\)]+)\)", description)
        if match:
            tags = match.group(1).split(',')
            for tag in tags:
                tag = tag.strip()
                if tag.startswith('T'):
                    attacks.append(MitreAttack(technique_id=tag))
                elif tag.startswith('TA'):
                    attacks.append(MitreAttack(tactic=tag))

        # 從 enrichments 提取 "T1071 - Application Layer Protocol"
        if enrichments:
            for e in enrichments:
                if ' - ' in e:
                    code, name = e.split(' - ', 1)
                    if code.startswith('T'):
                        attacks.append(MitreAttack(technique_id=code, technique_name=name))
                    elif code.startswith('TA'):
                        attacks.append(MitreAttack(tactic=code))
        
        return attacks

    def map(self, raw_data: Dict[str, Any]) -> MDRAlert:
        entities = []
        
        # 提取核心實體
        if raw_data.get("endpointName"):
            entities.append(MDREntity(type=EntityType.HOST, value=raw_data["endpointName"]))
            
        if raw_data.get("ipAddress"):
            entities.append(MDREntity(type=EntityType.IP, value=raw_data["ipAddress"]))
            
        if raw_data.get("userName"):
            entities.append(MDREntity(type=EntityType.USER, value=raw_data["userName"]))

        # 深入解析 Telemetry 資料
        telemetry_str = raw_data.get("telemetry")
        if telemetry_str:
            try:
                telemetry = json.loads(telemetry_str)
                event_type = telemetry.get("EventType")
                
                if telemetry.get("HashSHA256"):
                    entities.append(MDREntity(type=EntityType.FILE, value=telemetry["HashSHA256"], metadata={"algo": "sha256", "path": telemetry.get("Path")}))
                
                if event_type == 10: # Registry
                    reg_path = f"{telemetry.get('Hive')}\\\\{telemetry.get('Path')}\\\\{telemetry.get('Name')}"
                    entities.append(MDREntity(type=EntityType.DOMAIN, value=reg_path, metadata={"type": "registry", "value": telemetry.get("RegistryValue")}))
                
                if telemetry.get("PID"):
                    entities.append(MDREntity(type=EntityType.PROCESS, value=str(telemetry["PID"]), metadata={"name": telemetry.get("Name")}))
                    
            except:
                pass

        # 處理時間戳記
        ts_str = raw_data.get("createDate")
        timestamp = datetime.now()
        if ts_str:
            try:
                timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            except:
                pass

        return MDRAlert(
            alert_id=str(raw_data.get("id")),
            vendor="Fidelis Endpoint",
            tenant_id=self.tenant_id,
            timestamp=timestamp,
            severity=self._map_severity(raw_data.get("severity", 1)),
            title=raw_data.get("name", "Unknown Alert"),
            description=raw_data.get("description"),
            entities=entities,
            mitre_attack=self._parse_mitre(raw_data.get("description", ""), raw_data.get("enrichments", [])),
            enrichments=raw_data.get("enrichments", []) or [],
            raw_data=raw_data # 這裡先傳入原始資料，後續讓 Cleaner 處理
        )
