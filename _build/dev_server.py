#!/usr/bin/env python3
"""Local preview that mirrors Vercel's cleanUrls + trailingSlash routing.

  python3 _build/dev_server.py 8097

/services/ serves services.html, /blog/x/ serves blog/x/index.html, unknown paths get
404.html, and redirects from vercel.json are honored. /api/* is not emulated.
"""
import http.server
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDIRECTS = {r["source"].rstrip("/"): r["destination"] for r in json.load(open(os.path.join(ROOT, "vercel.json"))).get("redirects", [])}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]
        key = path.rstrip("/") or "/"
        if key in REDIRECTS:
            self.send_response(308)
            self.send_header("Location", REDIRECTS[key])
            self.end_headers()
            return
        fs = os.path.join(ROOT, path.lstrip("/"))
        if path.endswith("/") and path != "/":
            for cand in (fs.rstrip("/") + ".html", os.path.join(fs, "index.html")):
                if os.path.isfile(cand):
                    self.path = "/" + os.path.relpath(cand, ROOT)
                    return super().do_GET()
        elif path != "/" and not os.path.splitext(path)[1] and not os.path.exists(fs):
            self.send_response(308)
            self.send_header("Location", path + "/")
            self.end_headers()
            return
        if path == "/" or os.path.exists(fs):
            return super().do_GET()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(open(os.path.join(ROOT, "404.html"), "rb").read())

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8097
    http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
