"""
WSGI backend for Color-Distance Study on PythonAnywhere
- GET  /           -> serve web/index.html
- GET  /index.html -> same
- GET  /health     -> {"ok": true}
- POST /submit     -> JSON: {name, colorA, colorB, score}
                      append: ip \t timestamp \t name \t colorA \t colorB \t score
CORS: Access-Control-Allow-Origin: *
"""

import json
import os
import sys
import time

BASE_DIR = os.path.dirname(__file__)
INDEX_FILE = os.path.join(BASE_DIR, "web", "index.html")
OUTPUT_FILE = os.environ.get(
    "OUTPUT_FILE",
    os.path.join(BASE_DIR, "ratings.tsv"),
)

try:
    with open(INDEX_FILE, "rb") as f:
        INDEX_BODY = f.read()
except FileNotFoundError:
    INDEX_BODY = None


def _cors_headers(extra=None):
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
    ]
    if extra:
        headers.extend(extra)
    return headers


def application(environ, start_response):
    """WSGI entrypoint for PythonAnywhere."""
    method = (environ.get("REQUEST_METHOD") or "GET").upper()
    path = environ.get("PATH_INFO") or "/"

    # ---- CORS preflight ----
    if method == "OPTIONS":
        start_response("204 No Content", _cors_headers())
        return [b""]

    # ---- healthcheck ----
    if path == "/health" and method == "GET":
        start_response(
            "200 OK",
            _cors_headers([("Content-Type", "application/json; charset=utf-8")]),
        )
        return [b'{"ok": true}']

    # ---- Web app: web/index.html ----
    if path == "/" and method == "GET":
        if INDEX_BODY is None:
            start_response(
                "500 Internal Server Error",
                _cors_headers([("Content-Type", "text/plain; charset=utf-8")]),
            )
            return [b"index.html not found"]

        start_response(
            "200 OK",
            _cors_headers([("Content-Type", "text/html; charset=utf-8")]),
        )
        return [INDEX_BODY]

    # ---- API: Submit ----
    if path == "/submit" and method == "POST":
        try:
            length_str = environ.get("CONTENT_LENGTH") or "0"
            length = int(length_str)
            raw = environ["wsgi.input"].read(length) if length > 0 else b""
            data = json.loads(raw.decode("utf-8"))

            name = str(data.get("name", "")).strip()
            colorA = str(data.get("colorA", "")).strip()
            colorB = str(data.get("colorB", "")).strip()
            score = int(data.get("score"))

            if not name or not colorA or not colorB or not (0 <= score <= 100):
                raise ValueError("Invalid payload")

            ip = environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR", "-"))
            ts = int(time.time())
            line = f"{ip}\t{ts}\t{name}\t{colorA}\t{colorB}\t{score}\n"

            os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(line)

            # Log to stdout as JSON
            print(
                json.dumps(
                    {"ip": ip, "ts": ts, "name": name,
                     "A": colorA, "B": colorB, "score": score},
                    ensure_ascii=False,
                ),
                file=sys.stdout,
                flush=True,
            )

            start_response("204 No Content", _cors_headers())
            return [b""]

        except Exception as e:
            print(f"Error in /submit: {e}", file=sys.stderr, flush=True)
            start_response(
                "400 Bad Request",
                _cors_headers([("Content-Type", "application/json; charset=utf-8")]),
            )
            return [b'{"ok": false, "error": "bad_request"}']

    # ---- The rest: 404 ----
    start_response("404 Not Found", _cors_headers())
    return [b"not found"]
