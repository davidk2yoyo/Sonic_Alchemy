"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, canvas, voice, lyrics, projects

# Create FastAPI app
app = FastAPI(
    title="Sonic Alchemy API",
    description="AI-powered music creation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["authentication"])
app.include_router(canvas.router, prefix=settings.API_V1_PREFIX, tags=["canvas"])
app.include_router(voice.router, prefix=settings.API_V1_PREFIX, tags=["voice"])
app.include_router(lyrics.router, prefix=settings.API_V1_PREFIX, tags=["lyrics"])
app.include_router(projects.router, prefix=settings.API_V1_PREFIX, tags=["projects"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Sonic Alchemy API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
