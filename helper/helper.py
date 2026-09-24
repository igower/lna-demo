#!/usr/bin/env python3
"""Stand-in for a desktop helper like Box Tools: a local HTTP server a public web page talks to.

GET  /status          -> {"running": true, "version": "..."}; the page's install check.
POST /open?file=NAME  -> opens helper/files/NAME in its default desktop app.

Every request is printed as it arrives, so a denied request that still reached the helper is
visible here. Usage: python3 helper.py [--port 17300]
"""
import argparse
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FILES = Path(__file__).resolve().parent / "files"
VERSION = "1.0-demo"


class Handler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # Chrome's Private Network Access preflight asked for this; harmless elsewhere.
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/status":
            return self.reply(200, {"running": True, "version": VERSION})
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/open":
            return self.reply(404, {"error": "not found"})
        name = parse_qs(url.query).get("file", [""])[0]
        path = (FILES / name).resolve()
        if not name or path.parent != FILES or not path.is_file():
            return self.reply(404, {"error": f"no such file: {name}"})
        subprocess.Popen(["open", str(path)])
        self.reply(200, {"opened": name})

    def log_message(self, format, *args):
        origin = self.headers.get("Origin", "-") if hasattr(self, "headers") else "-"
        print(f"[helper] {self.command} {self.path}  from {origin}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=17300)
    port = parser.parse_args().port
    print(f"[helper] listening on http://127.0.0.1:{port}, serving {FILES}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
