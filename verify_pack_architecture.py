"""
Pack Architecture Verification Script

This script verifies the pack-based architecture is working correctly.
"""

import sys
import os
import io

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapter.core.pack_loader import get_pack_loader
from adapter.core.factory import AdapterFactory

def test_pack_discovery():
    """Test pack discovery"""
    print("=" * 60)
    print("Testing Pack Discovery")
    print("=" * 60)
    
    loader = get_pack_loader()
    packs = loader.discover_packs()
    
    print(f"✓ Discovered {len(packs)} packs: {', '.join(packs)}")
    return len(packs) > 0

def test_pack_metadata():
    """Test pack metadata loading"""
    print("\n" + "=" * 60)
    print("Testing Pack Metadata")
    print("=" * 60)
    
    loader = get_pack_loader()
    packs = loader.discover_packs()
    
    for pack in packs:
        try:
            metadata = loader.load_pack_metadata(pack)
            print(f"\n✓ {pack}:")
            print(f"  Display Name: {metadata.get('display_name')}")
            print(f"  Version: {metadata.get('version')}")
            print(f"  Capabilities: {', '.join(metadata.get('capabilities', []))}")
        except Exception as e:
            print(f"\n✗ {pack}: Failed to load metadata - {str(e)}")
            return False
    
    return True

def test_adapter_loading():
    """Test adapter loading"""
    print("\n" + "=" * 60)
    print("Testing Adapter Loading")
    print("=" * 60)
    
    # Test Fidelis adapter loading
    try:
        config = {
            "server_url": "https://test.example.com",
            "username": "test_user",
            "password": "test_pass",
            "fidelis_isolate_script_id": "script_001",
            "fidelis_terminate_process_script_id": "script_002"
        }
        
        adapter = AdapterFactory.get_adapter("Fidelis", "test_tenant", config)
        print(f"✓ Successfully loaded Fidelis adapter: {type(adapter).__name__}")
        
    except Exception as e:
        print(f"✗ Failed to load Fidelis adapter: {str(e)}")
        return False
    
    return True

def test_factory_list_vendors():
    """Test factory vendor listing"""
    print("\n" + "=" * 60)
    print("Testing Factory Vendor Listing")
    print("=" * 60)
    
    try:
        vendors = AdapterFactory.list_available_vendors()
        print(f"✓ Available vendors: {', '.join(vendors)}")
        return len(vendors) > 0
    except Exception as e:
        print(f"✗ Failed to list vendors: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PACK ARCHITECTURE VERIFICATION")
    print("=" * 60 + "\n")
    
    tests = [
        ("Pack Discovery", test_pack_discovery),
        ("Pack Metadata", test_pack_metadata),
        ("Adapter Loading", test_adapter_loading),
        ("Factory Vendor Listing", test_factory_list_vendors)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Pack architecture is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
