from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from database.connection import create_tables
from api.routes import auth, investigations, osint, reports

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting H4WK5INT OSINT Platform...")
    await create_tables()
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down H4WK5INT OSINT Platform...")

# Create FastAPI application
app = FastAPI(
    title="H4WK5INT OSINT Platform",
    description="Comprehensive OSINT (Open Source Intelligence) platform with Tor routing and advanced reporting",
    version=settings.version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(investigations.router, prefix="/api/investigations", tags=["Investigations"])
app.include_router(osint.router, prefix="/api/osint", tags=["OSINT Modules"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "operational",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )