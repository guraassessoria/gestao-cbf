import sys, os, traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.main import app
    handler = app
except Exception as e:
    # Captura o erro e expoe via endpoint de diagnostico
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse

    _error = traceback.format_exc()

    diag_app = FastAPI()

    @diag_app.get("/{path:path}")
    async def catch_all(path: str):
        return PlainTextResponse(f"STARTUP ERROR:\n{_error}", status_code=500)

    handler = diag_app
