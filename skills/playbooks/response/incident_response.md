# Playbook: Incident Response (資安事件應變)

## Description
當主機被確認感染時的標準應變程序 (SOP)。包含隔離、蒐證與通知。

## Instructions
你現在需要對受感染的主機 `{hostname}` 執行應變措施。

1. **立即隔離**: 呼叫 `isolate_endpoint` 切斷網路連線，防止擴散。
2. **確認狀態**: 再次呼叫 `get_host_details` (或類似工具) 確認主機雖已隔離但 Agent 仍連線。
3. **蒐證保留**: (模擬步驟) 建議使用者手動快照或執行蒐證腳本。
4. **最終報告**: 產出處置報告，包含執行時間與結果。

## Warning
執行隔離前，請確保該主機**不是**關鍵基礎設施 (如 AD Server)，除非威脅極高且已獲得授權。
