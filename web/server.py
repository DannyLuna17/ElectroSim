#!/usr/bin/env python3
"""
Simple HTTP server for serving the ElectroSim web application.
This serves the static files needed for the web version.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    """Start the web server."""
    # Change to web directory
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    PORT = 8000
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers for cross-origin requests
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # Add proper MIME types for Python files
            if self.path.endswith('.py'):
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
            
            super().end_headers()
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"ElectroSim Web Server")
        print(f"Serving at http://localhost:{PORT}")
        print(f"Directory: {web_dir}")
        print(f"Open http://localhost:{PORT}")
        print(f"Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()

