# Fidelis Endpoint 資源彙整與功能說明

本資料夾彙整了從 XSOAR 抽離出的 Fidelis Endpoint 相關資源，包含原始程式碼、API 定義以及自動化 Playbook。這些資源可用於理解 Fidelis 如何與 MDR 平台整合，並作為後續開發自動化回應 (Response) 策略的參考。

## 目錄結構與檔案說明

位於 `./resources` 目錄下：

| 檔案名稱 | 類型 | 說明 |
| :--- | :--- | :--- |
| `FidelisEndpoint.py` | Python 原始碼 | XSOAR 整合的原始邏輯，包含所有對伺服器的 API 呼叫實現。 |
| `FidelisEndpoint.yml` | API 定義 (XSOAR) | 定義了所有可用命令 (Commands)、輸入參數與輸出對應。 |
| `FidelisEndpoint_description.md` | 說明文件 | 整合的官方描述與基本組態說明。 |
| `playbook-Fidelis-Test.yml` | Playbook | 測試用剧本，展示了如何組合多個 API 命令進行自動化調查流程。 |

---

## 核心 API 功能與操作邏輯

透過分析 `FidelisEndpoint.yml`，以下是您可以實現的關鍵 API 操作：

### 1. 偵測與獲取 (Detection)
- **`fidelis-endpoint-list-alerts`**: 定期拉取資料庫中的告警資訊。
- **`fidelis-endpoint-get-alert-details`**: 針對特定告警獲取更深層的上下文。

### 2. 調查與獵捕 (Investigation & Hunting)
- **`fidelis-endpoint-list-processes`**: 即時獲取端點上正在執行的程序清單。
- **`fidelis-endpoint-query-events`**: 核心獵捕功能，可查詢：
  - **檔案 (File)**: 透過雜湊值 (Hash) 或檔名搜尋。
  - **網路 (Network)**: 查詢特定 IP 或網域名稱的連線記錄。
  - **DNS**: 查詢特定主機的網域解析記錄。

### 3. 事件回應與隔離 (Response & Containment)
這是 MDR 平台最關鍵的部分，可實現的「策略」包括：
- **`fidelis-endpoint-isolate-network`**: **網路隔離**。將受感染主機隔離，僅允許連線至指定的安全伺服器。
- **`fidelis-endpoint-remove-network-isolation`**: 解除隔離。
- **`fidelis-endpoint-kill-process`**: **終止程序**。遠端結束惡意程序。
- **`fidelis-endpoint-delete-file`**: **檔案刪除**。移除端點上的惡意檔案。
- **`fidelis-endpoint-get-file`**: **回傳檔案**。將端點上的可疑檔案拉回地端進行沙箱分析。

---

## 自動化策略建議 (MDR 整合方向)

您可以參考 `playbook-Fidelis-Test.yml` 的邏輯來設計您的 MDR 策略：

1.  **自動化富化 (Enrichment)**:
    - 當收到檔案告警時，自動觸發 `query-file-by-hash` 確認該檔案是否出現在企業內其他主機。
    - 自動調用 `host-info` 確認受影響端點的資產重要性。

2.  **主動防禦流程**:
    - **Step 1**: AI 判定告警為高風險。
    - **Step 2**: 自動執行 `isolate-network` 限制損害擴大。
    - **Step 3**: 執行 `get-file` 提取證據。
    - **Step 4**: 通知分析師進行最後確認。

---

## 如何使用本資料夾的資源？

- **參考開發**: 閱讀 `FidelisEndpoint.py` 中如何建構 API 請求的 Body。
- **擴充功能**: 如果您需要我們之前開發的 `fidelis_endpoint_client.py` 尚未具備的功能，可以參考 `FidelisEndpoint.yml` 的命令定義來新增方法。
- **策略設計**: 使用 `playbook-*.yml` 作為開發 AI 調度引擎 (AI Orchestration Engine) 的邏輯模板。
