import logging
import json
from typing import List, Dict, Any, Optional
from .models import BaseLLM
from adapter.core.schemas import MDRAlert

logger = logging.getLogger(__name__)

class MDRIntelligenceEngine:
    """
    MDR AI 調度引擎
    負責理解告警、決定行動並總結調查結果。
    """
    def __init__(self, llm: BaseLLM, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def investigate(self, alert: MDRAlert, registry: 'ToolRegistry', max_iterations: int = 5) -> str:
        """
        針對指定告警啟動自動化調查循環。
        """
        # 1. 準備工具 Schema
        tools = registry.get_schemas()
        
        # 2. 初始化對話
        alert_json = alert.model_dump_json(indent=2)
        user_message = f"偵測到一筆新的資安告警，請協助調查其根因並提供處置建議：\n\n{alert_json}"
        self.history.append({"role": "user", "content": user_message})

        logger.info(f"開始調查告警: {alert.alert_id} - {alert.title}")
        
        iterations = 0
        while iterations < max_iterations:
            iterations += 1
            logger.info(f"--- 迭代 {iterations} ---")
            
            response = self.llm.chat(self.history, tools=tools)
            message = response.choices[0].message
            
            # 將 AI 的回應加入歷史紀錄
            # 注意：OpenAI SDK 回傳的 message 物件可直接轉換為 dict 或按格式處理
            msg_dict = {"role": "assistant", "content": message.content}
            if hasattr(message, 'tool_calls') and message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            
            self.history.append(msg_dict)

            # 如果沒有工具呼叫，則這是最終結論
            if not (hasattr(message, 'tool_calls') and message.tool_calls):
                return message.content or "AI 調查完成，但未提供內容。"

            # 執行工具呼叫
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"執行工具: {func_name}({func_args})")
                try:
                    result = registry.execute(func_name, func_args)
                    # 如果結果是 Pydantic 模型或複雜物件，轉為 JSON 字串
                    if hasattr(result, "model_dump_json"):
                        result_str = result.model_dump_json()
                    else:
                        result_str = str(result)
                except Exception as e:
                    logger.error(f"工具執行失敗: {str(e)}")
                    result_str = f"Error: {str(e)}"

                # 將結果回饋給對話紀錄
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result_str
                })
        
        return "達到最大迭代次數，調查強制結束。請檢查目前對話紀錄。"
