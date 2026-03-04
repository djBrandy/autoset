#!/usr/bin/env python3
"""
AutoSET Demo - Showcase key features
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from autoset.tools.harvester import start_harvester
from autoset.tools.web_clone import clone_website
from autoset.utils.workspace import create_workspace
from autoset.utils.logging_setup import setup_logging

def demo():
    """Run AutoSET demo"""
    print("\n" + "="*60)
    print("AutoSET DEMO - AI-Powered Social Engineering Toolkit")
    print("="*60)
    
    # Setup
    setup_logging()
    workspace = create_workspace()
    print(f"\n📁 Workspace: {workspace}\n")
    
    # Demo 1: Credential Harvester
    print("="*60)
    print("DEMO 1: Credential Harvester")
    print("="*60)
    print("\n🎣 Starting credential harvester...")
    
    harvester = start_harvester(
        port=8082,
        output_file=str(workspace / "demo_creds.json"),
        redirect_url="https://example.com"
    )
    
    print(f"✅ Harvester running on http://localhost:8082")
    print(f"📊 Credentials will be saved to: {workspace / 'demo_creds.json'}")
    
    # Demo 2: Website Cloning
    print("\n" + "="*60)
    print("DEMO 2: Website Cloning")
    print("="*60)
    print("\n📥 Cloning example.com...")
    
    clone_dir = workspace / "demo_clone"
    result = clone_website("http://example.com", str(clone_dir))
    
    if result["success"]:
        print(f"✅ Website cloned to: {result['path']}")
        
        # List cloned files
        cloned_files = list(Path(result['path']).rglob("*"))
        print(f"📄 Cloned {len(cloned_files)} files")
    else:
        print(f"❌ Clone failed: {result.get('error')}")
    
    # Summary
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\n✅ AutoSET is fully functional!")
    print(f"\n📁 All demo files saved to: {workspace}")
    print("\nKey Features Demonstrated:")
    print("  ✅ Credential harvester server")
    print("  ✅ Website cloning")
    print("  ✅ Workspace isolation")
    print("  ✅ Logging system")
    print("\nAdditional Features Available:")
    print("  • AI-powered phishing email generation")
    print("  • Payload generation (msfvenom)")
    print("  • Ngrok tunneling")
    print("  • Multi-LLM support")
    print("\n🚀 Run 'python autoset/agent.py' to start the full interface")
    print("="*60)

if __name__ == "__main__":
    demo()
