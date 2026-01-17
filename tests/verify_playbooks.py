"""
Verify Playbooks - 驗證 PROMPT 劇本機制

測試 PlaybookLoader 與相關工具是否正常運作。
"""

import sys
import os
import json
import io

# 解決 Windows 編碼問題
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加入專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.playbook_loader import playbook_loader
from skills.registry import skills_registry
import skills.tools # 觸發註冊

def verify_playbook_system():
    print("=" * 60)
    print("PROMPT Playbook 機制驗證")
    print("=" * 60)

    # 1. 測試 Loader: 列出劇本
    print("\n[測試 1] 列出所有劇本 (Loader Direct Call)")
    playbooks = playbook_loader.list_playbooks()
    for pb in playbooks:
        print(f"  Found: {pb['name']} ({pb['category']}) - {pb['description'][:30]}...")
    
    if len(playbooks) >= 2:
        print("✅ 成功掃描到劇本檔案")
    else:
        print("❌ 未掃描到足夠的劇本檔案")
        return

    # 2. 測試 Loader: 讀取內容
    target_pb = "detailed_host_investigation"
    print(f"\n[測試 2] 讀取劇本內容: {target_pb}")
    content = playbook_loader.get_playbook_content(target_pb)
    
    if content and "# Playbook:" in content:
        print("✅ 成功讀取劇本內容")
        print(f"--- Content Preview ---\n{content[:100]}...\n-----------------------")
    else:
        print(f"❌ 讀取失敗或內容為空: {content}")

    # 3. 測試 Skills Registry Integration
    print("\n[測試 3] 透過 Tools Registry 呼叫")
    
    # 測試 list_playbooks 工具
    tools_list = skills_registry.execute_tool("list_playbooks")
    print(f"  Tool 'list_playbooks' returned {len(tools_list)} items.")

    # 測試 get_playbook 工具
    pb_result = skills_registry.execute_tool("get_playbook", playbook_name=target_pb)
    if "playbook_content" in pb_result:
        print("✅ Tool 'get_playbook' 執行成功")
    else:
        print(f"❌ Tool 'get_playbook' 執行失敗: {pb_result}")

    # 4. 驗證 Schema 存在
    schemas = skills_registry.get_tool_schemas()
    pb_tool_schema = next((s for s in schemas if s["function"]["name"] == "get_playbook"), None)
    
    if pb_tool_schema:
        print("\n✅ AI Tool Schema 'get_playbook' 存在")
    else:
        print("\n❌ AI Tool Schema 'get_playbook' 缺失")

    print("\n" + "=" * 60)
    print("驗證完成")
    print("=" * 60)

if __name__ == "__main__":
    verify_playbook_system()
