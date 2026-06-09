import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

class HTTPServer:
    def __init__(self, dashboard_path="dashboard.html"):
        self.dashboard_path = dashboard_path
        self.app = FastAPI()
        self.app.get("/")(self.serve_dashboard)

    async def serve_dashboard(self) -> HTMLResponse:
        with open(self.dashboard_path) as f:
            return HTMLResponse(f.read())

    def run(self):
        uvicorn.run(self.app, host="localhost", port=8000, log_level="warning")
