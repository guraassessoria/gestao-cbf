import sys, os, traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

try:
    from src.main import app  # noqa: F401 – Vercel detects `app` as ASGI entry
except Exception:
    _err = traceback.format_exc()
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_err}", status_code=500)
