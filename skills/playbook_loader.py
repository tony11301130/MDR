"""
Playbook Loader - PROMPT 劇本載入器

負責載入 Markdown 格式的劇本 (Prompts)，並提供給 AI Engine 使用。
"""

import os
import glob
from typing import Dict, List, Optional

class PlaybookLoader:
    def __init__(self, playbook_dir: str = None):
        if playbook_dir is None:
            # 預設為當前檔案所在目錄下的 playbooks 子目錄
            self.playbook_dir = os.path.join(os.path.dirname(__file__), "playbooks")
        else:
            self.playbook_dir = playbook_dir
            
    def list_playbooks(self) -> List[Dict[str, str]]:
        """
        列出所有可用的劇本
        
        Returns:
            劇本資訊列表，包含名稱與類別
        """
        playbooks = []
        # 遞迴搜尋所有 .md 檔案
        pattern = os.path.join(self.playbook_dir, "**", "*.md")
        files = glob.glob(pattern, recursive=True)
        
        for f in files:
            rel_path = os.path.relpath(f, self.playbook_dir)
            category = os.path.dirname(rel_path)
            # 檔名作為劇本名稱 (去除 .md)
            name = os.path.splitext(os.path.basename(f))[0]
            
            # 嘗試讀取第一行作為描述
            description = "No description"
            try:
                with open(f, "r", encoding="utf-8") as pf:
                    first_line = pf.readline().strip()
                    if first_line.startswith("#"):
                        description = first_line.lstrip("#").strip()
            except Exception:
                pass
                
            playbooks.append({
                "name": name,
                "category": category,
                "description": description,
                "path": rel_path
            })
            
        return playbooks

    def get_playbook_content(self, name: str) -> Optional[str]:
        """
        獲取指定劇本的完整內容
        
        Args:
            name: 劇本名稱 (不含路徑與副檔名)
            
        Returns:
            劇本內容字串，若找不到則回傳 None
        """
        # 搜尋符合名稱的檔案
        pattern = os.path.join(self.playbook_dir, "**", f"{name}.md")
        files = glob.glob(pattern, recursive=True)
        
        if not files:
            return None
            
        # 如果有多個同名檔案，取第一個 (通常不建議同名)
        target_file = files[0]
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading playbook {name}: {e}")
            return None

# 全局實例
playbook_loader = PlaybookLoader()
