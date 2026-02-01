"""
GreenPass Backend - Main Application Entry Point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.core.router import router as core_router
from src.geo.router import router as geo_router
from src.env.router import router as env_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GreenPass EUDR API",
    description="Compliance-as-a-Service for EUDR Agro-Exports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger.info("Starting GreenPass EUDR API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(core_router, prefix="/api", tags=["Core - Projects & Reports"])
app.include_router(geo_router, prefix="/geo", tags=["Geo - Spatial Analysis"])
app.include_router(env_router, prefix="/env", tags=["Env - Environmental Analysis"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GreenPass EUDR API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "external_apis": {
            "gfw": "available",
            "openmeteo": "available",
            "climatiq": "requires_key"
        }
    }
