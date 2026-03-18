import sys, os, traceback

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

_diag_info = f"ROOT={_root}\nFILES_IN_ROOT={os.listdir(_root)[:20]}\nSRC_EXISTS={os.path.isdir(os.path.join(_root, 'src'))}\nPYTHON={sys.version}\n"

try:
    from src.main import app
except Exception:
    _err = traceback.format_exc()
    print(f"STARTUP FAILURE:\n{_diag_info}\n{_err}", file=sys.stderr, flush=True)
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_diag_info}\n{_err}", status_code=500)

handler = app
