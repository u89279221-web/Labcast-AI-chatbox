"""
Main application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logging
from app.core.database import create_db_and_tables
from app.routers.machine import router as machine_router
from app.routers.device import router as device_router
from app.routers.auth import router as auth_router
from app.routers.document import router as document_router
from app.routers.maintenance import router as maintenance_router
from app.routers import machine, auth, device, document, maintenance, analytics, ws
from app.models.device import Device
from app.models.user import User
from app.chatbot.embeddings import initialize_embeddings
from app.core.limiter import limiter, request_var
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Runs on startup and shutdown.
    """
    create_db_and_tables()
    initialize_embeddings()
    ws.start_mqtt_bridge(asyncio.get_running_loop())
    yield

app = FastAPI(
    title="LabCast AI Backend",
    description="Backend API for LabCast AI using FastAPI and SQLModel.",
    version="0.1.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def store_request_middleware(request: Request, call_next):
    token = request_var.set(request)
    try:
        response = await call_next(request)
        return response
    finally:
        request_var.reset(token)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Register routers
app.include_router(auth_router)
app.include_router(machine_router)
app.include_router(device_router)
# Mount the document router under /api/machine so endpoints match /api/machine/{machine_id}/documents
app.include_router(document.router, prefix="/api/machine", tags=["document"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["maintenance"])
app.include_router(analytics.router)
app.include_router(ws.router)

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/admin")
def get_admin():
    """
    Serve the admin dashboard HTML file.
    """
    return FileResponse("app/static/admin.html")

@app.get("/chat")
def get_chat():
    """
    Serve the mobile-friendly student chat interface.
    """
    return FileResponse("app/static/chat.html")

@app.get("/")
def read_root() -> dict[str, str]:
    """
    Root endpoint for health check.
    """
    return {"message": "Welcome to LabCast AI Backend API"}
