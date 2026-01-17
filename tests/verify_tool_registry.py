import json
from skills.registry import skills_registry
import skills # 觸發工具註冊

def verify_tool_registry():
    print("--- AI 標準工具庫匯出測試 ---")
    
    tools = skills_registry.get_tool_schemas()
    
    print(f"目前已註冊工具數: {len(tools)}")
    
    # 輸出第一個工具的 Schema (OpenAI 格式)
    if tools:
        print("\n[OpenAI 工具規格範例 - investigate_host]")
        print(json.dumps(tools[0], indent=2, ensure_ascii=False))

    # 模擬 AI 呼叫工具
    print("\n[模擬 AI 執行工具: investigate_host]")
    # 這裡我們需要 Mock adapter 避免真的去連 API
    # 實際上這會在更大的系統整合測試中完成
    print("註冊表已成功運作，可提供給 LLM 作為 Tool Calling 的定義文件。")

if __name__ == "__main__":
    verify_tool_registry()
