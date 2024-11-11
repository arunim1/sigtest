import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class LoggingHandler(BaseHTTPRequestHandler):
    def _handle_request(self):
        # Log request details
        timestamp = datetime.now().isoformat()
        request_info = {
            "timestamp": timestamp,
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
            "client_address": self.client_address[0],
        }
        
        print(f"Request: {json.dumps(request_info, indent=2)}")

        # Send a simple response
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Request logged")

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), LoggingHandler)
    print("Starting logging server on port 8000...")
    server.serve_forever()
