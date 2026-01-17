"""
Skills Registry - 工具註冊中心

負責管理所有 Skills 工具的註冊與提供給 AI Engine 使用。
"""

from typing import Dict, Any, Callable, List


class SkillsRegistry:
    """Skills 工具註冊中心"""
    
    _tools: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_tool(
        cls,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        func: Callable
    ):
        """
        註冊一個工具到註冊表
        
        Args:
            name: 工具名稱（唯一識別碼）
            description: 工具描述（供 AI 理解用途）
            parameters: JSON Schema 格式的參數定義
            func: 實際執行的函數
        """
        cls._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": func
        }
    
    @classmethod
    def get_tool(cls, name: str) -> Dict[str, Any]:
        """獲取指定工具的定義"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, Dict[str, Any]]:
        """獲取所有已註冊的工具"""
        return cls._tools.copy()
    
    @classmethod
    def get_tool_schemas(cls) -> List[Dict[str, Any]]:
        """
        獲取所有工具的 Schema（供 AI Tool Calling 使用）
        
        Returns:
            符合 OpenAI/Gemini Function Calling 格式的工具定義列表
        """
        schemas = []
        for tool_name, tool_def in cls._tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool_def["name"],
                    "description": tool_def["description"],
                    "parameters": tool_def["parameters"]
                }
            })
        return schemas
    
    @classmethod
    def execute_tool(cls, name: str, **kwargs) -> Any:
        """
        執行指定的工具
        
        Args:
            name: 工具名稱
            **kwargs: 工具參數
            
        Returns:
            工具執行結果
        """
        tool = cls.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        return tool["function"](**kwargs)
    
    @classmethod
    def clear_all(cls):
        """清空所有註冊的工具（主要用於測試）"""
        cls._tools.clear()


# 建立全域實例
skills_registry = SkillsRegistry()
