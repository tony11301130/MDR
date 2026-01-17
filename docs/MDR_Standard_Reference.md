# MDR 標準規範參考 (Standard Reference)

本文件為開發者提供統一的資料結構 (Schema) 與工具庫 (Tool Library) 定義。

## 1. 資料標準化規格 (Data Schemas)

### 1.1. 通用告警模型 (MDRAlert)
| 欄位 | 說明 | 範例 |
| :--- | :--- | :--- |
| **alert_id** | 唯一辨識碼 | UUID 或 Vendor-Specific ID |
| **timestamp** | 事件發生時間 | ISO8601 UTC (2024-01-01T12:00:00Z) |
| **tenant_id** | 租戶 ID | tenant-123 |
| **source** | 來源廠商 | Fidelis, TrendMicro |
| **severity** | 嚴重程度 | CRITICAL, HIGH, MEDIUM, LOW |
| **entities** | 關鍵實體清單 | 包含 Host, IP, User, File 等物件 |

### 1.2. 實體定義 (MDREntity)
統一表示環境中的對象，以便 AI 進行跨產品關聯分析。

## 2. 標準工具庫 (Standard Tool Library)
定義處理層提供給 AI 分析層的工具介面 (Tool Calling)。

### 2.1. 內容富化 (Enrichment)
*   `get_threat_intel(indicator)`: 查詢外部威脅情資。
*   `get_whois_info(indicator)`: 查詢網域或 IP 註冊資訊。

### 2.2. 環境上下文 (Contextual)
*   `get_alert_history(entity_id)`: 取得實體過去 30 天的告警統計。
*   `get_process_prevalence(hash)`: 查詢檔案雜湊在環境中出現的頻次。
*   `get_asset_importance(hostname)`: 從 CMDB 獲取主機重要度評等。

### 2.3. 即時鑑識 (Forensic)
*   `list_processes(hostname)`: 獲取主機目前的執行程序列表。
*   `get_process_tree(hostname, pid)`: 追蹤特定程序的父子關係。
*   `list_network_connections(hostname)`: 獲取主機目前的網路連線狀態。

### 2.4. 回應處置 (Response)
*   `isolate_host(hostname)`: 執行網路隔離。
*   `terminate_process(hostname, pid)`: 強制終止惡意程序。
*   `quarantine_file(hostname, file_path)`: 隔離惡意檔案。
*   `block_ip(ip_address)`: 在防火牆或 EDR 下發阻擋策略。

## 3. 實作建議
*   **Data Cleaning**: Adapter 應剔除無意義的 Meta Data，降低 LLM 運算成本。
*   **Idempotency**: 處置動作 (如 Block IP) 需確保重複執行不會出錯。
