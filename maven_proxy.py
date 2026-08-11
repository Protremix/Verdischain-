#!/usr/bin/env python3
"""Local Maven + Pub proxy — bridges Java/Gradle/Dart to dl.google.com, pub.dev, and Flutter artifacts"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import os
import hashlib
import ssl

CACHE_DIR = "/opt/maven-cache"

class ProxyHandler(BaseHTTPRequestHandler):
    def _resolve_url(self, path):
        if path.startswith("/google/"):
            return "https://dl.google.com" + path[len("/google"):]
        elif path.startswith("/maven-central/"):
            return "https://repo1.maven.org/maven2" + path[len("/maven-central"):]
        elif path.startswith("/pub/"):
            return "https://pub.dev" + path[len("/pub"):]
        elif path.startswith("/gradle/"):
            return "https://services.gradle.org" + path[len("/gradle"):]
        elif path.startswith("/flutter-io/"):
            return "https://storage.googleapis.com/download.flutter.io" + path[len("/flutter-io"):]
        return None

    def _fetch(self, url):
        """Returns (data, status_code). data is bytes or None."""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        cache_subdir = os.path.join(CACHE_DIR, cache_key[:2])
        cache_file = os.path.join(cache_subdir, cache_key)
        
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return (f.read(), 200)
        
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*"
            })
            ctx = ssl.create_default_context()
            resp = urllib.request.urlopen(req, timeout=60, context=ctx)
            data = resp.read()
            os.makedirs(cache_subdir, exist_ok=True)
            with open(cache_file, "wb") as f:
                f.write(data)
            print("OK: " + url + " (" + str(len(data)) + " bytes)", flush=True)
            return (data, 200)
        except urllib.error.HTTPError as e:
            print("HTTP " + str(e.code) + ": " + url, flush=True)
            return (None, e.code)
        except Exception as e:
            print("ERR: " + url + " -> " + str(e), flush=True)
            return (None, 502)

    def _content_type(self, path):
        if path.endswith(".pom") or path.endswith(".module"):
            return "application/xml"
        elif path.endswith(".jar"):
            return "application/java-archive"
        elif path.endswith(".json") or "/api/packages" in path:
            return "application/json"
        elif path.endswith(".tar.gz"):
            return "application/gzip"
        elif path.endswith(".zip"):
            return "application/zip"
        return "application/octet-stream"

    def do_GET(self):
        path = self.path
        url = self._resolve_url(path)
        if not url:
            self.send_error(404, "Unknown: " + path)
            return
        
        data, status = self._fetch(url)
        if data is None:
            self.send_error(status, "Upstream returned " + str(status))
            return
        
        # Only rewrite URLs in pub.dev JSON API responses
        if path.startswith("/pub/") and "/api/packages" in path:
            try:
                text = data.decode("utf-8")
                text = text.replace("https://pub.dev", "http://localhost:8888/pub")
                data = text.encode("utf-8")
            except:
                pass
        
        self.send_response(200)
        self.send_header("Content-Type", self._content_type(path))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self):
        path = self.path
        url = self._resolve_url(path)
        if not url:
            self.send_error(404, "Unknown: " + path)
            return
        
        data, status = self._fetch(url)
        if data is None:
            self.send_error(status, "Upstream returned " + str(status))
            return
        
        self.send_response(200)
        self.send_header("Content-Type", self._content_type(path))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)
    server = HTTPServer(("127.0.0.1", 8888), ProxyHandler)
    print("Maven+Pub proxy running on http://localhost:8888", flush=True)
    server.serve_forever()
