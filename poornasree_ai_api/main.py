"""
Poornasree AI Chatbot API
========================

Main application entry point with organized structure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Try organized imports, fallback to original
try:
    from src.api.routes import chat, documents, health, ai, service_guide
    print("Using organized route imports")
except ImportError:
    # Fallback to original imports if organization not complete
    from app.routes import chat, documents, health, ai, service_guide
    print("Using original route imports (fallback)")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    try:
        print("Poornasree AI API started successfully!")
        print("Ready to process machine manuals and answer questions")
    except Exception as e:
        print(f"Failed to initialize services: {e}")
    
    yield
    
    # Shutdown
    print("Poornasree AI API shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Poornasree AI Chatbot API",
    description="Google Gemini 2.5 Flash-Lite powered chatbot API for machine manuals",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(service_guide.router, prefix="/api/v1/service-guide", tags=["Service Guide"])
app.include_router(ai.router, tags=["AI Management"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Poornasree AI Chatbot API",
        "version": "3.0.0",
        "status": "running",
        "ai_model": "Google Gemini 2.5 Flash-Lite",
        "documentation": "/docs",
        "health": "/health",
        "structure": "organized"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
