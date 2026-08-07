from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import nodes, bots, deploy, monitor

app = FastAPI(title="EarnApp Dashboard Master V2")

# Mount Routers
app.include_router(nodes.router, prefix="/api/nodes", tags=["Nodes"])
app.include_router(bots.router, prefix="/api/bots", tags=["Bots"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["Deploy"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["Monitor"])

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
