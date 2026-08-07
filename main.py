import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import nodes, bots, deploy, monitor, auth as auth_router, settings as settings_router
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.auth import verify_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="EarnApp Dashboard Master V2")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.url.path not in ["/api/auth/login", "/api/auth/check"]:
        token = request.cookies.get("ea_token")
        if not token or not verify_token(token):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

# Mount Routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["Nodes"])
app.include_router(bots.router, prefix="/api/bots", tags=["Bots"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["Deploy"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["Monitor"])

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    import argparse
    import os

    parser = argparse.ArgumentParser(description="EarnApp Cluster Dashboard V2")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port to run the dashboard on (default: 8000)")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
