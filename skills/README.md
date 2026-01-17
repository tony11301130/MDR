# Skills Layer - API 劇本層

## 概述

Skills 層是 MDR 系統的業務邏輯編排層，位於 Adapter 層與 AI Engine 之間。它負責將多個 Adapter 原子操作組合成完整的調查劇本，以降低 AI 的呼叫次數並提升分析效率。

## 架構定位

```
AI Engine (分析層)
    ↓ 呼叫 Skills
Skills Layer (劇本層) ← 你在這裡
    ↓ 呼叫 Adapter
Adapter Layer (資料清洗層)
    ↓ 呼叫 Vendor API
Vendor API (底層 API)
```

## 目錄結構

```
skills/
├── __init__.py              # 模組初始化
├── registry.py              # 工具註冊中心
├── README.md                # 本文件
├── investigation/           # 調查類劇本
│   ├── __init__.py
│   ├── host_investigation.py
│   └── network_investigation.py (待實作)
├── response/                # 處置類劇本
│   ├── __init__.py
│   └── isolation.py
└── enrichment/              # 富化類劇本
    ├── __init__.py
    └── threat_intel.py (待實作)
```

## Skills 分類

### 1. Investigation (調查類)

複合式調查劇本，整合多個資料源進行深度分析：

- **主機調查** (`host_investigation.py`): 獲取行程、網路連線、主機資訊
- **網路調查** (待實作): 分析網路流量、連線關聯
- **檔案分析** (待實作): 檔案雜湊、簽章驗證、沙箱分析

### 2. Response (處置類)

自動化處置動作，執行安全防護措施：

- **主機隔離** (`isolation.py`): 隔離/解除隔離受感染主機
- **行程終止** (待實作): 終止惡意行程
- **IP/Domain 封鎖** (待實作): 在防火牆層級封鎖威脅

### 3. Enrichment (富化類)

資料富化與情資比對：

- **情資比對** (待實作): VirusTotal, AlienVault 等情資庫查詢
- **資產上下文** (待實作): 查詢 CMDB 獲取資產資訊
- **歷史關聯** (待實作): 關聯歷史告警與事件

## 使用方式

### 註冊工具

```python
from skills.registry import skills_registry

def my_custom_skill(tenant_id: str, target: str):
    # 你的劇本邏輯
    return {"result": "success"}

# 註冊到註冊表
skills_registry.register_tool(
    name="my_custom_skill",
    description="我的自訂劇本",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
            "target": {"type": "string"}
        },
        "required": ["tenant_id", "target"]
    },
    func=my_custom_skill
)
```

### AI Engine 調用

```python
from skills.registry import skills_registry

# 獲取所有工具的 Schema
tool_schemas = skills_registry.get_tool_schemas()

# 傳給 AI
response = ai_engine.investigate(
    alert=alert,
    available_tools=tool_schemas
)

# 執行 AI 選擇的工具
result = skills_registry.execute_tool(
    name="investigate_host",
    tenant_id="tenant_001",
    hostname="DESKTOP-ABC"
)
```

## 設計原則

### 1. 單一職責

每個 Skill 應該專注於一個明確的業務目標，例如：
- ✅ `deep_investigate_host()` - 深度調查主機
- ❌ `do_everything()` - 做所有事情

### 2. 跨 Adapter 協作

Skills 可以同時調用多個不同廠商的 Adapter：

```python
def correlate_edr_and_firewall(tenant_id: str, ip: str):
    # 查詢 EDR
    edr_adapter = AdapterFactory.get_adapter("Fidelis", tenant_id, config)
    hosts = edr_adapter.search_by_ip(ip)
    
    # 查詢防火牆
    fw_adapter = AdapterFactory.get_adapter("PaloAlto", tenant_id, config)
    connections = fw_adapter.get_connections(ip)
    
    # 關聯分析
    return correlate(hosts, connections)
```

### 3. 結果精簡

Skills 應該過濾雜訊，只回傳 AI 需要的關鍵資訊：

```python
# ❌ 不好的做法：回傳所有原始資料
return {"all_processes": [1000+ processes]}

# ✅ 好的做法：只回傳可疑項目與摘要
return {
    "suspicious_processes": [5 processes],
    "summary": "發現 5 個可疑行程，建議隔離主機"
}
```

## 開發指南

### 新增一個 Skill

1. 選擇合適的分類目錄（investigation/response/enrichment）
2. 建立新的 Python 檔案
3. 實作 Skill 函數
4. 在 `__init__.py` 中匯出
5. 在對應的註冊點註冊工具

### 測試 Skill

建立對應的測試腳本：

```python
# test_my_skill.py
from skills.investigation.my_skill import my_skill_function

result = my_skill_function(tenant_id="test", target="test_host")
print(result)
```

## 與 Adapter 的差異

| 特性 | Adapter Layer | Skills Layer |
|------|---------------|--------------|
| **職責** | 資料清洗與標準化 | 業務邏輯編排 |
| **操作粒度** | 原子操作（單一 API 呼叫） | 複合操作（多步驟劇本） |
| **廠商相依** | 強相依（每個 Pack 對應一個廠商） | 廠商無關（可跨多個 Adapter） |
| **AI 調用** | 不直接調用 | 直接調用 |
| **範例** | `get_host_details()` | `deep_investigate_host()` |

## 未來規劃

- [ ] 實作網路調查劇本
- [ ] 實作情資比對劇本（VirusTotal）
- [ ] 實作自動化修復劇本
- [ ] 支援劇本版本管理
- [ ] 支援劇本執行歷程追蹤
