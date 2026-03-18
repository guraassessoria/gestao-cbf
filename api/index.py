from fastapi import FastAPI

app = FastAPI()


@app.get("/api/{path:path}")
@app.get("/{path:path}")
async def test(path: str):
    return {"status": "ok", "path": path}
