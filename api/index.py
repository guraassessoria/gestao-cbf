import sys, os

# Wrap EVERYTHING to prevent any unhandled exception
_err_text = None
app = None

try:
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _root)

    from fastapi import FastAPI as _FastAPI
    from fastapi.responses import PlainTextResponse as _PTR

    try:
        from src.main import app
    except Exception:
        import traceback
        _err_text = traceback.format_exc()
except Exception:
    import traceback
    _err_text = f"OUTER IMPORT FAIL:\n{traceback.format_exc()}"

if app is None:
    try:
        from fastapi import FastAPI as _FA2
        from fastapi.responses import PlainTextResponse as _PTR2
        app = _FA2()

        @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def catch_all(path: str):
            return _PTR2(
                f"STARTUP ERROR:\nROOT={_root}\nPYTHON={sys.version}\n\n{_err_text or 'unknown'}",
                status_code=500,
            )
    except Exception:
        # Last resort: raw ASGI app
        async def app(scope, receive, send):
            if scope["type"] == "http":
                body = f"FATAL: {_err_text or 'unknown'}".encode()
                await send({"type": "http.response.start", "status": 500, "headers": [[b"content-type", b"text/plain"]]})
                await send({"type": "http.response.body", "body": body})

handler = app
