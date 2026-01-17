from typing import List, Dict, Any, Callable
import inspect

class ToolMetadata:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class ToolRegistry:
    """
    標準工具庫註冊表
    提供工具發現機制，讓 AI 層能動態獲取可用功能及其詮釋資料。
    """
    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        self._tools[name] = ToolMetadata(name, description, parameters, func)

    def get_all_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_tool() for tool in self._tools.values()]

    def execute_tool(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found")
        return self._tools[name].func(**kwargs)

# 全域註冊實例
tool_registry = ToolRegistry()
