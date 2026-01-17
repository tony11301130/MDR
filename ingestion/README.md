# Ingestion Service (觸發器層) 開發指南

本目錄包含 MDR 系統的「觸發器 (Ingestion)」相關邏輯。
其主要職責為：**主動輪詢外部告警來源 -> 過濾去重 -> 觸發 AI 調查**。

## 📁 目錄結構 (預計)

```
ingestion/
├── README.md           # 本文件 (開發指南)
├── scheduler.py        # 排程器 (每分鐘執行一次 Polling)
├── deduplication.py    # 過濾器 (負責比對是否為重複告警)
├── worker.py           # 背景工作 (負責呼叫 AI Engine)
└── main.py             # (選用) 若需提供 API 介面可保留 FastAPI
```

## 🚀 開發步驟 (Step-by-Step)

### 步驟 1: 建立基礎排程服務 (Polling Service)
- **目標**: 建立一個能持續運作的迴圈 (Loop)，每 60 秒醒來一次。
- **檔案**: `ingestion/scheduler.py`
- **實作重點**:
    - 使用 Python `time.sleep(60)` 或 `APScheduler`。
    - 確保程式不會因為單次錯誤而崩潰 (Try-Catch)。
- **驗證方式**: 執行程式，觀察 Console 是否每分鐘印出 `[INFO] Polling cycle started...`。

### 步驟 2: 實作 Fidelis 輪詢邏輯
- **目標**: 讓排程器真正去呼叫 Fidelis API 撈取資料。
- **檔案**: 更新 `ingestion/scheduler.py`
- **實作重點**:
    - 整合 `FidelisEndpointClient`。
    - 記錄 `last_check_time` (上次檢查時間)，只撈 `startDate > last_check_time` 的告警。
    - 處理 API 連線失敗的重試機制。
- **驗證方式**: 執行程式，確認能印出從 Fidelis 撈回來的 Raw JSON Data。

### 步驟 3: 串接 Adapter 進行資料標準化
- **目標**: 將廠商原始 JSON 轉為 MDR 標準格式 (`MDRAlert`)。
- **檔案**: `ingestion/scheduler.py` 或 `ingestion/adapter_glue.py`
- **實作重點**:
    - 使用 `MDRAlert` Pydantic Model 進行驗證。
    - 確保必要欄位 (Title, Severity, Entity) 都有正確解析。
- **驗證方式**: 觀察 Log，確認印出的是乾淨的 `MDRAlert(id=..., title=...)` 物件。

### 步驟 4: 實作具備記憶的篩選器 (Stateful Deduplication)
- **目標**: 避免同一告警在短時間內重複觸發 AI。
- **檔案**: `ingestion/deduplication.py`
- **實作重點**:
    - **指紋 (Fingerprint)**: `md5(Title + Hostname + TenantID)`。
    - **記憶體快取**: 使用 `Dict` 記錄 `seen_alerts = {hash: timestamp}`。
    - **邏輯**: 若 `check_time - seen_time < 30 mins` 則視為重複，回傳 `Skip`。
- **驗證方式**:
    1. 第一次傳入告警 A -> 回傳 "New"。
    2. 立即再傳入告警 A -> 回傳 "Duplicate"。
    3. 等待 30 分鐘後 (或手動改時間) 再傳入告警 A -> 回傳 "New"。

### 步驟 5: 背景觸發 AI 引擎 (End-to-End)
- **目標**: 將通過篩選的告警送交給大腦 (AI Engine)。
- **檔案**: `ingestion/worker.py`
- **實作重點**:
    - 初始化 `MDRIntelligenceEngine`。
    - 呼叫 `engine.investigate(alert)`。
    - 將調查結果簡單輸出到檔案或 Log。
- **驗證方式**: 
    1. 啟動 `scheduler.py`。
    2. 等待或模擬產生一個新告警。
    3. 確認 Console 出現 AI 的思考過程 ("Thinking...", Tool calls 等)。

---

## 🛠️ 架構決策紀錄

1.  **為什麼用 Polling (輪詢)?**
    - 因為 Fidelis API 是被動的，不支援 Webhook 主動通知。
    - 我們需要控制檢查頻率 (避免打爆 API)。

2.  **為什麼需要 Deduplication (去重)?**
    - 避免「告警風暴 (Alert Storm)」導致 AI Token 費用爆炸。
    - MVP 階段先使用 **In-Memory** 記憶，重啟後會歸零 (可接受)。未來可升級為 Redis。
