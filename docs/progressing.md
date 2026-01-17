# MDR 專案開發進度表 (progressing.md)

本文件用於追蹤 MDR 系統的開發狀態。每個模組皆以「可獨立驗證」為拆分原則。

## ⏳ 專案狀態總覽
- **開發階段**: Phase 0 (核心框架) → 即將進入 Phase 1 (租戶管理)
- **當前重點**: 核心框架已完成，準備實作租戶管理與告警接收層
- **最新更新**: 2026-01-18 - 確認核心架構與 Skills 實作完整，準備進入 Phase 1 (租戶/接收)

---

## ✅ 已完成模組 (Completed)

### 1. 系統設計與標準化
- [x] **四層架構定義**: 確立 Vendor API, Adapter, Skill, AI Engine 的分層邏輯 (`MDR_Core_Platform.md`)。
- [x] **通用資料模型 (Schema)**: 實作 Pydantic 版的 `MDRAlert`、`MDREntity`、`MDRProcess` 等標準化資料結構。
- [x] **標準工具介面定義**: 定義 AI 可呼叫的標準工具函數簽章與註冊機制。

### 2. AI 分析核心 (AI Orchestration Engine)
- [x] **AI 編排引擎核心**: 實作 `MDRIntelligenceEngine` 的自動化調查循環邏輯 (`ai_orchestration_engine/core/engine.py`)。
- [x] **OpenAI 整合模組**: 支援 GPT-4 等模型的 API 對接。
- [x] **Gemini 整合模組**: 針對 Python 3.8 實作 `requests` 版的穩定對接，支援 Gemini-1.5-Flash。
- [x] **工具註冊中心 (Tool Registry)**: 實作動態工具註冊與 AI Tool Calling 映射機制（雙重註冊表架構）。

### 3. 產品轉接器 (Adapter Layer)
- [x] **Fidelis API 邏輯驗證**: 完成由 XSOAR 抽離至獨立 Sandbox (`Fidelis-Endpoint api test/`) 的驗證。
- [x] **Fidelis 原始資料抓取器**: 正式封裝 `fidelis_client.py` 並整合至系統（含執行腳本、隔離主機等能力）。
- [x] **Fidelis 資料清洗器**: 實作 `fidelis_adapter.py` 與 `fidelis_mapper.py`，完成標準化映射。
- [x] **Pack-based 架構重構**: 將 Adapter 重構為類似 XSOAR Content 的 Pack 結構 (`adapter/packs/`)，支援模組化廠商整合。
- [x] **Adapter 核心框架**: 實作 `BaseAdapter`、`AdapterFactory`、`PackLoader` 等核心元件。
- [x] **TrendMicro 範例 Pack**: 建立第二個廠商 Pack 以驗證多廠商架構。

### 4. API 劇本層 (Skill/Playbook Layer) - **已建立混合架構**
- [x] **深度主機調查劇本**: 實作 `deep_investigate_host()` 複合式調查邏輯 (`skills/investigation/host_investigation.py`)。
- [x] **告警初篩劇本**: 實作 `triage_alert()` 自動富化功能。
- [x] **標準工具封裝**: 實作 `investigate_host`、`isolate_endpoint`、`list_endpoint_processes` 等標準工具 (`skills/tools.py`)。
- [x] **Skills 目錄重構**: 將 Skills 層從 `adapter/skills/` 遷移至獨立的 `skills/` 目錄，建立 investigation/response/enrichment 三大分類。
- [x] **工具註冊系統**: 實作 `SkillsRegistry` 統一管理所有 Skills 工具。
- [x] **PROMPT 劇本支援**: 實作 `PlaybookLoader` 與 Markdown 格式劇本，支援 AI 讀取自然語言指令。
- [ ] **情資比對劇本**: 尚未實作 VirusTotal 或其他情資庫對接。
- [ ] **網路調查劇本**: 尚未實作網路連線分析與 IP 情資查詢。

### 5. 開發環境與測試
- [x] **Windows 編碼修復**: 強制 UTF-8 輸出，解決 Emoji 與繁體中文顯示問題。
- [x] **整合測試指令碼**: 實作 `test_ai_orchestration.py` 可進行端到端模擬測試。
- [x] **Adapter 驗證腳本**: 建立多個驗證腳本 (`verify_adapter.py`, `verify_pack_architecture.py` 等)。

---

## 🔄 進行中模組 (In Progress)

### 1. API 劇本層擴展
- [ ] **實作網路調查劇本**: 建立網路連線分析與 IP 情資查詢劇本。
- [ ] **實作情資比對劇本**: 整合 VirusTotal 或其他情資庫進行自動化分析。

---

## 📅 尚未開始模組 (Pending / To-Do)

### 1. 租戶與數據持久化 (Phase 1 優先)
- [ ] **租戶管理員 (Tenant Manager)**: 負責租戶建立、API Key 管理與後端隔離邏輯。
- [ ] **PostgreSQL 隔離實作**: 實作 Schema-per-tenant 資料庫架構，確保數據隱私。
- [ ] **基礎告警接收 (Ingestion)**: 實作接收外部 Webhook 或 API Pull 的基礎接收點。
- [ ] **告警持久化**: 將標準化後的告警存入資料庫，支援歷史查詢與審計。

### 1.5 觸發器系統 (Trigger System) - **待補 (Pending)**
- [ ] **排程觸發器 (Polling Trigger)**: 針對不支援 Webhook 的廠商 (如 Fidelis API)，實作定期 Polling 機制。
- [ ] **Webhook 觸發器**: 接收外部推播事件並標準化為內部 Event。
- [ ] **手動觸發 API**: 允許分析師或測試腳本手動啟動針對特定主機/告警的調查。
- [ ] **觸發過濾規則**: 定義「什麼樣的告警值得調查」的過濾邏輯 (Filter Logic)。

### 2. 處置與通知
- [ ] **自動化處置模組 (Response Actions)**: 實作 EDR 隔離主機、封鎖 IP 的真實 API 呼叫（目前已有 Fidelis 隔離，需擴展至其他廠商）。
- [ ] **多平台通知服務 (Notify Service)**: 實作 Line, Telegram, Email 的通知發送邏輯。
- [ ] **處置審計日誌**: 記錄所有自動化處置動作，支援合規稽核。

### 3. 高可用與監控
- [ ] **訊息隊列 (Kafka/Message Bus)**: 導入訊息緩衝，處理大流量告警與非同步分析。
- [ ] **FastAPI 網關**: 封裝為 RESTful API 提供給前端或外部調用。
- [ ] **健康檢查與監控**: 實作系統健康檢查端點與 Prometheus 指標。

### 4. 前端視覺化
- [ ] **分析師控制台 (Analyst Dashboard)**: 顯示告警、調查流程與決策建議的 Web 介面。
- [ ] **調查歷程視覺化**: 展示 AI 的推理過程與工具呼叫鏈。

### 5. 其他廠商整合
- [ ] **XSOAR Adapter**: 整合 XSOAR 作為編排平台。
- [ ] **Firewall Adapter**: 整合防火牆（Palo Alto, Fortinet 等）。
- [ ] **SIEM Adapter**: 整合 SIEM 產品（Splunk, QRadar 等）。

---

## 📊 開發完成度統計

| 層級 | 完成度 | 狀態 |
|------|--------|------|
| **底層 API (Vendor)** | 30% | Fidelis 完成，其他廠商待整合 |
| **資料清洗層 (Adapter)** | 80% | 核心框架完成，需擴展更多廠商 |
| **API 劇本層 (Skills)** | 60% | 架構重構完成，需擴展更多劇本 |
| **分析層 (AI Engine)** | 90% | 核心邏輯完成，待整合更多 Skills |
| **租戶管理** | 0% | 尚未開始 |
| **告警接收 (Ingestion)** | 0% | 尚未開始 |
| **通知服務** | 0% | 尚未開始 |
| **前端介面** | 0% | 尚未開始 |

**整體完成度**: ~40%

---

## 🎯 下一步建議 (Next Steps)

1. **擴展 Skills 劇本** (2-3 天)
   - 實作情資比對劇本 (VirusTotal)
   - 實作網路調查劇本
   - 實作自動化處置劇本

2. **實作租戶管理** (3-5 天)
   - 建立 `tenant_manager/` 模組
   - 實作 PostgreSQL Schema-per-tenant 隔離
   - 建立租戶配置管理 API

3. **實作告警接收層** (2-3 天)
   - 建立 `ingestion/` 模組
   - 實作 Webhook 接收端點
   - 實作告警持久化邏輯

4. **整合 AI Engine 與 Skills** (1-2 天)
   - 更新 AI Engine 使用新的 SkillsRegistry
   - 測試端到端的 AI 調查流程
