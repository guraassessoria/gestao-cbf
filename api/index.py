from http.server import BaseHTTPRequestHandler
import sys, os, traceback

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

errors = []

try:
    from fastapi import FastAPI
    errors.append("fastapi: OK")
except Exception:
    errors.append(f"fastapi: FAIL\n{traceback.format_exc()}")

try:
    from src.core.config import get_settings
    errors.append("config: OK")
except Exception:
    errors.append(f"config: FAIL\n{traceback.format_exc()}")

try:
    from src.core.db import engine
    errors.append("db: OK")
except Exception:
    errors.append(f"db: FAIL\n{traceback.format_exc()}")

try:
    from src.main import app
    errors.append("main: OK")
except Exception:
    errors.append(f"main: FAIL\n{traceback.format_exc()}")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        body = f"ROOT={_root}\nPYTHON={sys.version}\nPATH_EXISTS={os.path.isdir(os.path.join(_root,'src'))}\n\n" + "\n---\n".join(errors)
        self.wfile.write(body.encode())
