import sys, os, traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

_startup_error = None

try:
    from src.main import app
except Exception:
    _startup_error = traceback.format_exc()
    _err = _startup_error or "Unknown startup error"
    app = FastAPI()

    @app.get("/{path:path}")
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_err}", status_code=500)

handler = app
