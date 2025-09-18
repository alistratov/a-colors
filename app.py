"""
Minimal backend for Color‑Distance Study
- Standard library only
- Accepts POST /submit with JSON: {name, colorA, colorB, score}
- Appends a TSV line to ratings.tsv: name colorA colorB score\n
CORS enabled for simplicity (Access-Control-Allow-Origin: *).
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import time


OUTPUT_FILE = os.environ.get('OUTPUT_FILE', 'ratings.tsv')
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '28080'))


class Handler(BaseHTTPRequestHandler):
    server_version = "ColorDistance/1.0"

    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/submit':
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(length) if length else b''
            data = json.loads(raw.decode('utf-8'))
            name = str(data.get('name', '')).strip()
            colorA = str(data.get('colorA', '')).strip()
            colorB = str(data.get('colorB', '')).strip()
            score = int(data.get('score'))
            if not name or not colorA or not colorB or not (0 <= score <= 100):
                raise ValueError('invalid payload')
        except Exception:
            self.send_response(400)
            self._set_cors()
            self.end_headers()
            return

        # Append TSV line
        line = f"{name}\t{colorA}\t{colorB}\t{score}\n"
        # Ensure directory exists if path includes folders
        os.makedirs(os.path.dirname(OUTPUT_FILE) or '.', exist_ok=True)
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(line)

        self.send_response(204)  # No Content
        self._set_cors()
        self.end_headers()

    # Quieter logs
    def log_message(self, fmt, *args):
        # Uncomment to see access logs:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt%args))
        # pass


if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"Listening on http://{HOST}:{PORT} → writing to {OUTPUT_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down…")
