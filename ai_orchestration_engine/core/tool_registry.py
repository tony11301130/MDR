import inspect
from typing import Dict, Any, List, Callable
from adapter.core.base_adapter import BaseAdapter

class ToolRegistry:
    """
    負責將 Adapter 的方法註冊並轉換為 LLM Tool Schema。
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register_adapter(self, adapter: BaseAdapter):
        """
        掃描 Adapter 中具備調查能力的方法並進行註冊。
        目前手動定義需要公開給 AI 的方法，未來可改為 Decorator。
        """
        target_methods = [
            "list_processes",
            "isolate_host",
            "terminate_process",
            "get_host_details"
        ]

        for method_name in target_methods:
            if hasattr(adapter, method_name):
                method = getattr(adapter, method_name)
                schema = self._generate_openai_schema(method_name, method)
                self._tools[method_name] = method
                self._schemas.append(schema)

    def _generate_openai_schema(self, name: str, func: Callable) -> Dict[str, Any]:
        """
        根據函式簽章自動生成 OpenAI Tool Schema。
        """
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or "No description provided."
        
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ['self']: continue
            
            # 這裡簡化處理，預設為 string，實務上可根據 type hint 優化
            properties[param_name] = {
                "type": "string" if param.annotation == str else "string",
                "description": f"Parameter {param_name}"
            }
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def get_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name in self._tools:
            return self._tools[name](**arguments)
        raise ValueError(f"Tool {name} not found in registry.")
