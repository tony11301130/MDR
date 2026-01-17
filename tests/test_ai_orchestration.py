import os
import sys
import io
from datetime import datetime
from dotenv import load_dotenv

# 解決 Windows 環境下 print 內容包含 Emoji 或特殊字元時的編碼問題
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 將專案路徑加入 sys.path 以便 import 模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_orchestration_engine.core.models import OpenAILLM, GeminiLLM
from ai_orchestration_engine.core.engine import MDRIntelligenceEngine
from ai_orchestration_engine.core.tool_registry import ToolRegistry
from adapter.core.schemas import MDRAlert, Severity, MDREntity, EntityType

def test_ai_connection():
    # 1. 載入環境變數
    env_path = os.path.join("ai_orchestration_engine", ".env")
    load_dotenv(env_path)
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL", "gpt-4o")

    if not api_key or "your_api_key_here" in api_key:
        print("❌ 錯誤: 請先在 ai_orchestration_engine/.env 檔案中填入正確的 OPENAI_API_KEY")
        return

    print(f"🚀 正在使用模型 {model} 進行連線測試...")

    # 2. 初始化 LLM 與 引擎
    try:
        # 根據環境變數決定使用哪個 LLM
        if "gemini" in model.lower():
            llm = GeminiLLM(api_key=api_key, model=model)
        else:
            llm = OpenAILLM(api_key=api_key, model=model)
            
        registry = ToolRegistry() # 暫不註冊真實工具，僅測試 AI 邏輯
        
        system_prompt = (
            "你是一個專業的資安分析大腦 (MDR Intelligence Engine)。"
            "你的任務是分析告警並決定是否需要進一步調查。"
            "請用繁體中文回答。"
        )
        engine = MDRIntelligenceEngine(llm=llm, system_prompt=system_prompt)

        # 3. 建立一個模擬告警 (Mock Alert)
        mock_alert = MDRAlert(
            alert_id="ALERT-123",
            vendor="Fidelis",
            tenant_id="Tenant-A",
            timestamp=datetime.now(),
            severity=Severity.HIGH,
            title="偵測到惡意行程執行",
            description="主機 PC-01 執行了 PowerShell 下載腳本，疑似為 Cobalt Strike 活動。",
            entities=[
                MDREntity(type=EntityType.HOST, value="PC-01"),
                MDREntity(type=EntityType.PROCESS, value="powershell.exe")
            ]
        )

        print("\n--- 正在發送測試告警給 AI ---")
        print(f"告警標題: {mock_alert.title}")
        
        # 4. 執行調查
        result = engine.investigate(alert=mock_alert, registry=registry)
        
        print("\n✅ AI 回應成功：")
        print("-" * 30)
        print(result)
        print("-" * 30)

    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    test_ai_connection()
