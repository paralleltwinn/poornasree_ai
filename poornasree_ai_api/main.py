from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from app.routes import chat, documents, health, ai, service_guide
from app.services.ai_service import AIService
from app.database import test_database_connection, init_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AI service globally
ai_service = AIService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    try:
        # Test database connection
        db_connected = await test_database_connection()
        if db_connected:
            # Initialize database tables
            try:
                await init_database()
                print("✅ Database initialized successfully!")
            except Exception as db_error:
                print(f"⚠️  Database table creation issue: {db_error}")
                print("   Tables may already exist - continuing...")
        else:
            print("⚠️  Database connection failed - some features may not work")
        
        # Initialize AI models
        await ai_service.initialize()
        print("🚀 Poornasree AI API started successfully!")
        print("📚 Ready to process machine manuals and answer questions")
        print("🗄️  MySQL Database connected and ready!")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        print("⚠️  API will start but some features may not work properly")
    
    yield
    
    # Shutdown
    print("👋 Poornasree AI API shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Poornasree AI Chatbot API",
    description="Google Gemini 2.5 Flash-Lite powered chatbot API for machine manuals - Enhanced with complete Gemini integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for Flutter web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
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
        "version": "2.0.0",
        "status": "running",
        "ai_model": "Google Gemini 2.5 Flash-Lite (Entirely Integrated)",
        "features": [
            "Google Gemini 2.5 Flash-Lite AI-powered responses with complete integration",
            "Machine manual Q&A",
            "Document upload and processing", 
            "Advanced AI conversation capabilities",
            "Multi-format document support (PDF, DOCX, TXT, XLSX)",
            "Excel multiple sheets processing",
            "Service Guide training and management",
            "Row-wise Excel data processing",
            "MySQL database integration",
            "Chat history and user management",
            "AI status monitoring and testing"
        ],
        "endpoints": {
            "health": "/health",
            "ai_status": "/api/v1/ai/status",
            "chat": "/api/v1/chat",
            "upload": "/api/v1/documents/upload",
            "service_guide": "/api/v1/service-guide",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
