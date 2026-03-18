import sys, os, traceback

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

try:
    from src.main import app
except Exception:
    _err = traceback.format_exc()
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_err}", status_code=500)

handler = app
