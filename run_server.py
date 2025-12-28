"""
Simple HTTP Server for EPF Visualizer
Run this script to start a local web server
"""

import http.server
import socketserver
import webbrowser
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress logging for common 404s (favicon, browser extensions)
        if len(args) > 0 and isinstance(args[0], str):
            if args[0].startswith('GET /v1/') or args[0].startswith('GET /favicon.ico'):
                return  # Don't log these
        # Log everything else
        super().log_message(format, *args)

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 80)
        print(f"🚀 EPF Visualizer Server Started!")
        print("=" * 80)
        print(f"\n📍 Server running at: http://localhost:{PORT}")
        print(f"📂 Serving files from: {os.getcwd()}")
        print("\n✨ Opening browser...")
        print("\n⚠️  Press Ctrl+C to stop the server\n")
        print("=" * 80)
        
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}/index.html')
        
        # Start server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            print("=" * 80)

if __name__ == "__main__":
    run_server()
