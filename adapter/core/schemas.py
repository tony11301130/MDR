from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class EntityType(str, Enum):
    HOST = "HOST"
    IP = "IP"
    FILE = "FILE"
    PROCESS = "PROCESS"
    USER = "USER"
    DOMAIN = "DOMAIN"

class MDREntity(BaseModel):
    type: EntityType
    value: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MitreAttack(BaseModel):
    tactic: Optional[str] = None
    technique_id: Optional[str] = None
    technique_name: Optional[str] = None

class MDRAlert(BaseModel):
    alert_id: str
    vendor: str
    tenant_id: str
    timestamp: datetime
    severity: Severity
    title: str
    description: Optional[str] = None
    entities: List[MDREntity] = Field(default_factory=list)
    mitre_attack: List[MitreAttack] = Field(default_factory=list)
    enrichments: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class MDRProcess(BaseModel):
    pid: int
    ppid: Optional[int] = None
    name: str
    command_line: Optional[str] = None
    executable_path: Optional[str] = None
    username: Optional[str] = None
    start_time: Optional[datetime] = None
    hash: Optional[Dict[str, str]] = None  # e.g., {"md5": "...", "sha256": "..."}

class MDRToolResult(BaseModel):
    status: str  # "success" or "error"
    data: Any
    message: Optional[str] = None
    execution_time: float

