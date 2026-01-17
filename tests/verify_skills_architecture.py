"""
Skills Architecture Verification Script

驗證新的 Skills 架構是否正常運作。
"""

import sys
import os
import io

# 解決 Windows 環境下 print 內容包含 Emoji 或特殊字元時的編碼問題
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 確保可以 import 專案模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_skills_structure():
    """驗證 Skills 目錄結構"""
    print("=" * 60)
    print("階段一：驗證目錄結構")
    print("=" * 60)
    
    required_paths = [
        "skills/__init__.py",
        "skills/registry.py",
        "skills/tools.py",
        "skills/investigation/__init__.py",
        "skills/investigation/host_investigation.py",
        "skills/response/__init__.py",
        "skills/response/isolation.py",
        "skills/enrichment/__init__.py",
    ]
    
    all_exist = True
    for path in required_paths:
        full_path = os.path.join(os.path.dirname(__file__), path)
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"{status} {path}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("\n✅ 所有必要檔案都存在")
    else:
        print("\n❌ 部分檔案缺失")
        return False
    
    return True


def verify_imports():
    """驗證 Import 是否正常"""
    print("\n" + "=" * 60)
    print("階段二：驗證 Import 路徑")
    print("=" * 60)
    
    try:
        # 測試 Skills Registry
        from skills.registry import SkillsRegistry, skills_registry
        print("✅ skills.registry 匯入成功")
        
        # 測試調查類劇本
        from skills.investigation.host_investigation import deep_investigate_host, triage_alert
        print("✅ skills.investigation.host_investigation 匯入成功")
        
        # 測試處置類劇本
        from skills.response.isolation import isolate_endpoint, unisolate_endpoint
        print("✅ skills.response.isolation 匯入成功")
        
        # 測試工具註冊模組
        import skills.tools
        print("✅ skills.tools 匯入成功（工具註冊已觸發）")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import 失敗: {e}")
        return False


def verify_tool_registration():
    """驗證工具註冊"""
    print("\n" + "=" * 60)
    print("階段三：驗證工具註冊")
    print("=" * 60)
    
    try:
        from skills.registry import skills_registry
        import skills  # 觸發工具註冊
        
        # 獲取所有已註冊的工具
        all_tools = skills_registry.get_all_tools()
        tool_schemas = skills_registry.get_tool_schemas()
        
        print(f"\n已註冊工具數量: {len(all_tools)}")
        print("\n已註冊的工具列表:")
        for tool_name in all_tools.keys():
            tool_def = all_tools[tool_name]
            print(f"  • {tool_name}: {tool_def['description']}")
        
        # 驗證預期的工具都已註冊
        expected_tools = [
            "investigate_host",
            "triage_alert",
            "list_endpoint_processes",
            "isolate_endpoint",
            "unisolate_endpoint"
        ]
        
        missing_tools = []
        for tool_name in expected_tools:
            if tool_name not in all_tools:
                missing_tools.append(tool_name)
        
        if missing_tools:
            print(f"\n❌ 缺少以下工具: {missing_tools}")
            return False
        else:
            print("\n✅ 所有預期工具都已註冊")
        
        # 驗證 Schema 格式
        print("\n驗證工具 Schema 格式:")
        for schema in tool_schemas[:2]:  # 只檢查前兩個
            if "type" in schema and "function" in schema:
                func = schema["function"]
                if "name" in func and "description" in func and "parameters" in func:
                    print(f"  ✅ {func['name']} - Schema 格式正確")
                else:
                    print(f"  ❌ {func.get('name', 'Unknown')} - Schema 格式錯誤")
                    return False
            else:
                print(f"  ❌ Schema 缺少必要欄位")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 工具註冊驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_no_circular_imports():
    """驗證沒有循環依賴"""
    print("\n" + "=" * 60)
    print("階段四：驗證無循環依賴")
    print("=" * 60)
    
    try:
        # 嘗試 import 所有模組
        import skills
        from adapter.core.factory import AdapterFactory
        from adapter.core.base_adapter import BaseAdapter
        
        print("✅ 無循環依賴問題")
        return True
        
    except ImportError as e:
        print(f"❌ 發現循環依賴: {e}")
        return False


def main():
    """主驗證流程"""
    print("\n" + "=" * 60)
    print("Skills 架構驗證腳本")
    print("=" * 60 + "\n")
    
    results = []
    
    # 執行各階段驗證
    results.append(("目錄結構", verify_skills_structure()))
    results.append(("Import 路徑", verify_imports()))
    results.append(("工具註冊", verify_tool_registration()))
    results.append(("循環依賴", verify_no_circular_imports()))
    
    # 總結
    print("\n" + "=" * 60)
    print("驗證結果總結")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有驗證都通過！Skills 架構重構成功！")
    else:
        print("⚠️  部分驗證失敗，請檢查上方錯誤訊息")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
