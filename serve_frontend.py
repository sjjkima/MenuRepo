#!/usr/bin/env python3
"""
Simple static file server for the frontend pages in this project root.
Run this to serve the site on localhost:8080
"""
import http.server
import os
import socketserver

PORT = 8080
FRONTEND_DIR = os.path.dirname(__file__)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[FRONTEND] {format % args}")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


print(f"Frontend server: http://localhost:{PORT}")
print(f"Customer menu:   http://localhost:{PORT}/customer.html?table=1")
print(f"Reception:       http://localhost:{PORT}/admin.html")
print(f"Analytics:       http://localhost:{PORT}/analytics.html")

with ReusableTCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
