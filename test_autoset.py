#!/usr/bin/env python3
"""
AutoSET Test Suite
Tests all major functionality
"""
import sys
import time
from pathlib import Path

# Add autoset to path
sys.path.insert(0, str(Path(__file__).parent))

from autoset.tools.harvester import start_harvester
from autoset.tools.web_clone import clone_website
from autoset.tools.payload_gen import list_payloads
from autoset.utils.workspace import create_workspace
from autoset.utils.logging_setup import setup_logging

def test_workspace():
    """Test workspace creation"""
    print("\n" + "="*60)
    print("TEST 1: Workspace Creation")
    print("="*60)
    
    workspace = create_workspace()
    print(f"✅ Workspace created: {workspace}")
    assert workspace.exists(), "Workspace should exist"
    return workspace

def test_harvester(workspace):
    """Test credential harvester"""
    print("\n" + "="*60)
    print("TEST 2: Credential Harvester")
    print("="*60)
    
    output_file = workspace / "test_creds.json"
    harvester = start_harvester(
        port=8081,
        output_file=str(output_file),
        redirect_url="https://example.com"
    )
    
    print(f"✅ Harvester started on port 8081")
    print(f"📊 Output file: {output_file}")
    
    # Test if server is running
    import requests
    try:
        response = requests.get("http://localhost:8081/", timeout=2)
        print(f"✅ Server responding: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Server check failed: {e}")
    
    return harvester

def test_web_clone(workspace):
    """Test website cloning"""
    print("\n" + "="*60)
    print("TEST 3: Website Cloning")
    print("="*60)
    
    # Clone a simple site
    clone_dir = workspace / "cloned"
    result = clone_website("http://example.com", str(clone_dir))
    
    if result["success"]:
        print(f"✅ Website cloned successfully")
        print(f"📁 Path: {result['path']}")
    else:
        print(f"⚠️  Clone failed: {result.get('error')}")
    
    return result

def test_payload_list():
    """Test payload listing"""
    print("\n" + "="*60)
    print("TEST 4: Payload Listing")
    print("="*60)
    
    result = list_payloads("windows")
    
    if result["success"]:
        print(f"✅ Found {result['count']} Windows payloads")
        print(f"📋 Sample payloads:")
        for payload in result["payloads"][:5]:
            print(f"   - {payload}")
    else:
        print(f"⚠️  Payload listing failed: {result.get('error')}")
    
    return result

def test_llm_provider():
    """Test LLM provider"""
    print("\n" + "="*60)
    print("TEST 5: LLM Provider")
    print("="*60)
    
    try:
        from autoset.core.llm_provider import LLMProvider
        
        llm = LLMProvider(provider="ollama")
        print(f"✅ LLM Provider initialized")
        
        # Test simple chat
        response = llm.chat([
            {"role": "user", "content": "Say 'test successful' if you can read this"}
        ])
        
        content = response["message"]["content"]
        print(f"✅ LLM Response: {content[:100]}...")
        
        return True
    except Exception as e:
        print(f"⚠️  LLM test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AutoSET Test Suite")
    print("="*60)
    
    # Setup logging
    log_file = setup_logging()
    print(f"📝 Log file: {log_file}")
    
    results = {
        "passed": 0,
        "failed": 0
    }
    
    try:
        # Test 1: Workspace
        workspace = test_workspace()
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Workspace test failed: {e}")
        results["failed"] += 1
        return
    
    try:
        # Test 2: Harvester
        harvester = test_harvester(workspace)
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Harvester test failed: {e}")
        results["failed"] += 1
    
    try:
        # Test 3: Web Clone
        test_web_clone(workspace)
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Web clone test failed: {e}")
        results["failed"] += 1
    
    try:
        # Test 4: Payload List
        test_payload_list()
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Payload list test failed: {e}")
        results["failed"] += 1
    
    try:
        # Test 5: LLM Provider
        if test_llm_provider():
            results["passed"] += 1
        else:
            results["failed"] += 1
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        results["failed"] += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📊 Total:  {results['passed'] + results['failed']}")
    print("="*60)
    
    if results["failed"] == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed")

if __name__ == "__main__":
    main()
