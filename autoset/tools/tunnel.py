"""Ngrok tunneling tool for public access"""
import logging
import subprocess
import time
import requests
import json

logger = logging.getLogger(__name__)

class NgrokTunnel:
    """Ngrok tunnel manager"""
    
    def __init__(self, port: int, protocol: str = "http"):
        self.port = port
        self.protocol = protocol
        self.process = None
        self.public_url = None
    
    def start(self) -> dict:
        """Start ngrok tunnel
        
        Returns:
            dict with public URL
        """
        try:
            # Start ngrok
            cmd = ["ngrok", self.protocol, str(self.port), "--log=stdout"]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel to establish
            time.sleep(3)
            
            # Get public URL from ngrok API
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                data = response.json()
                
                if data.get("tunnels"):
                    self.public_url = data["tunnels"][0]["public_url"]
                    logger.info(f"Ngrok tunnel established: {self.public_url}")
                    
                    return {
                        "success": True,
                        "public_url": self.public_url,
                        "local_port": self.port,
                        "message": f"Tunnel active: {self.public_url}"
                    }
            except Exception as e:
                logger.error(f"Failed to get ngrok URL: {e}")
            
            return {
                "success": False,
                "error": "Could not retrieve public URL",
                "message": "Tunnel may be starting, check manually"
            }
            
        except Exception as e:
            logger.error(f"Ngrok start failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Ngrok start failed"
            }
    
    def stop(self):
        """Stop ngrok tunnel"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            logger.info("Ngrok tunnel stopped")
    
    def get_url(self) -> str:
        """Get public URL"""
        return self.public_url


def start_tunnel(port: int, protocol: str = "http") -> NgrokTunnel:
    """Start ngrok tunnel
    
    Args:
        port: Local port to tunnel
        protocol: Protocol (http, tcp)
        
    Returns:
        NgrokTunnel instance
    """
    tunnel = NgrokTunnel(port, protocol)
    result = tunnel.start()
    
    if result["success"]:
        return tunnel
    else:
        raise Exception(f"Tunnel failed: {result.get('error')}")
