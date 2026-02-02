"""
USA Sector Rotation Dashboard - FastAPI Backend
Adapted from KRX system for US market
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
PROJECT_ROOT = BACKEND_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Create FastAPI app
app = FastAPI(
    title="USA Sector Rotation Dashboard",
    description="Three-Layer Framework: Cohesion + Regime + Trend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from routers import sector_rotation, breakout, network, signals

# Include routers
app.include_router(sector_rotation.router, prefix="/api/overview", tags=["Overview"])
app.include_router(breakout.router, prefix="/api/breakout", tags=["Breakout"])
app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])

# Serve static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    """Serve the main dashboard page"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "USA Sector Rotation Dashboard API", "docs": "/docs"}


@app.get("/{page}.html")
async def serve_page(page: str):
    """Serve HTML pages"""
    page_path = FRONTEND_DIR / f"{page}.html"
    if page_path.exists():
        return FileResponse(page_path)
    return {"error": "Page not found"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "usa-sector-rotation",
        "data_dir": str(DATA_DIR),
        "data_available": DATA_DIR.exists()
    }


@app.get("/api/status")
async def api_status():
    """API status with data file info"""
    from datetime import datetime

    # Find latest data files
    data_files = {}
    if DATA_DIR.exists():
        for pattern in ["actionable_tickers_*.csv", "consolidated_ticker_analysis_*.json"]:
            files = sorted(DATA_DIR.glob(pattern), reverse=True)
            if files:
                data_files[pattern.replace("*", "LATEST")] = {
                    "path": str(files[0]),
                    "modified": datetime.fromtimestamp(files[0].stat().st_mtime).isoformat()
                }

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "data_files": data_files,
        "endpoints": [
            "/api/overview/summary",
            "/api/overview/top-picks",
            "/api/overview/theme-health",
            "/api/breakout/candidates",
            "/api/breakout/stages",
            "/api/network/search",
            "/api/network/graph-data",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
