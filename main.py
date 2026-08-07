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

if __name__ == "__main__":
    import uvicorn
    import argparse
    import os

    parser = argparse.ArgumentParser(description="EarnApp Cluster Dashboard V2")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port to run the dashboard on (default: 8000)")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
