from typing import Dict, Any, List, Set

class DataCleaner:
    """
    負責實作 MDR 流程中的「資料清洗」層級。
    目標：剔除冗餘欄位、縮減 Token 消耗、過濾雜訊。
    """
    
    @staticmethod
    def clean_dict(data: Dict[str, Any], exclude_keys: Set[str] = None) -> Dict[str, Any]:
        """
        遞迴清理字典，移除空值與排除的 Key。
        """
        if exclude_keys is None:
            exclude_keys = {"links", "self", "href", "metadata_version"} # 預設排除常見冗餘 Key
            
        cleaned = {}
        for k, v in data.items():
            if k in exclude_keys or v is None:
                continue
            
            if isinstance(v, dict):
                inner = DataCleaner.clean_dict(v, exclude_keys)
                if inner: cleaned[k] = inner
            elif isinstance(v, list):
                inner_list = []
                for item in v:
                    if isinstance(item, dict):
                        c_item = DataCleaner.clean_dict(item, exclude_keys)
                        if c_item: inner_list.append(c_item)
                    else:
                        inner_list.append(item)
                if inner_list: cleaned[k] = inner_list
            else:
                cleaned[k] = v
        return cleaned

    @staticmethod
    def optimize_for_ai(data: Dict[str, Any], event_type: str = "generic") -> Dict[str, Any]:
        """
        針對 AI 分析進行額外的優化。
        動態篩選關鍵欄位，大幅減少 Token 消耗。
        """
        # 定義不同類型事件的「必備診斷欄位」
        DIAGNOSTIC_WHITELIST = {
            "file": {"name", "path", "hash", "sha256", "md5", "action", "size", "process_name"},
            "process": {"pid", "ppid", "name", "command_line", "executable_path", "user"},
            "registry": {"path", "hive", "name", "value", "action"},
            "network": {"source_ip", "dest_ip", "source_port", "dest_port", "protocol", "domain"},
            "generic": {"id", "type", "severity", "title", "description", "timestamp"}
        }

        # 這裡的邏輯可以進一步擴展，例如針對長 String 進行摘要
        if not isinstance(data, dict):
            return data

        # 基礎策略：僅保留特定 Key，或根據 event_type 篩選
        # 為了保持彈性，我們合併通用欄位與特定類型欄位
        allowed_keys = DIAGNOSTIC_WHITELIST["generic"]
        if event_type in DIAGNOSTIC_WHITELIST:
            allowed_keys = allowed_keys.union(DIAGNOSTIC_WHITELIST[event_type])

        # 執行過濾
        optimized = {}
        for k, v in data.items():
            # 模糊匹配或精確匹配 Key
            k_lower = k.lower()
            if any(key in k_lower for key in allowed_keys):
                if isinstance(v, dict):
                    optimized[k] = DataCleaner.optimize_for_ai(v, event_type)
                elif isinstance(v, list):
                    optimized[k] = [
                        DataCleaner.optimize_for_ai(item, event_type) if isinstance(item, dict) else item 
                        for item in v
                    ]
                else:
                    optimized[k] = v
        
        return optimized
