import sys, os, traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

_startup_error = None
_app = None

try:
    from src.main import app as _app
except Exception:
    _startup_error = traceback.format_exc()

if _app is not None:
    handler = _app
else:
    _err = _startup_error or "Unknown startup error"
    diag = FastAPI()

    @diag.get("/{path:path}")
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_err}", status_code=500)

    handler = diag
