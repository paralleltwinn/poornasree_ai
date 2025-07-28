from fastapi import APIRouter
from datetime import datetime
import time
import os
import psutil
import pytz
from app.models import HealthCheck

router = APIRouter()
start_time = time.time()

# Indian Standard Time timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current time in Indian Standard Time"""
    return datetime.now(IST)

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint to verify API status
    """
    uptime = time.time() - start_time
    
    # Check AI service status
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        ai_status = "healthy" if ai_service.initialized else "initializing"
    except Exception:
        ai_status = "error"
    
    # Check database/storage status
    try:
        # Check if data directory exists and is writable
        data_dir = "./data"
        if os.path.exists(data_dir) and os.access(data_dir, os.W_OK):
            db_status = "healthy"
        else:
            db_status = "warning"
    except Exception:
        db_status = "error"
    
    return HealthCheck(
        status="healthy",
        timestamp=get_indian_time(),
        version="1.0.0",
        uptime=uptime,
        ai_model_status=ai_status,
        database_status=db_status
    )

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with system information
    """
    try:
        uptime = time.time() - start_time
        
        # System information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # AI service status
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()
            ai_detailed = ai_service.get_status()
        except Exception as e:
            ai_detailed = {"error": str(e)}
        
        # Document service status
        try:
            from app.services.document_service import DocumentService
            doc_service = DocumentService()
            doc_stats = doc_service.get_upload_stats()
        except Exception as e:
            doc_stats = {"error": str(e)}
        
        return {
            "status": "healthy",
            "timestamp": get_indian_time(),
            "version": "1.0.0",
            "uptime_seconds": uptime,
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "system": {
                "memory_used_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_used_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "services": {
                "ai_service": ai_detailed,
                "document_service": doc_stats
            },
            "features": {
                "chat": "operational",
                "document_upload": "operational",
                "vector_search": "operational",
                "free_tier": True
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": get_indian_time(),
            "error": str(e)
        }

@router.get("/health/ai")
async def ai_health_check():
    """
    Specific health check for AI services
    """
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        if not ai_service.initialized:
            return {
                "status": "initializing",
                "message": "AI service is starting up...",
                "timestamp": get_indian_time().isoformat()
            }
        
        # Test AI functionality with a simple query
        test_result = await ai_service.chat("test")
        
        ai_status = ai_service.get_status()
        
        return {
            "status": "healthy",
            "message": "AI service is fully operational",
            "timestamp": get_indian_time().isoformat(),
            "test_response_time": test_result.get("processing_time"),
            "model_info": {
                "model_name": ai_status.get("model_name", "poornasree-simple-ai"),
                "document_count": ai_status.get("document_count", 0),
                "capabilities": ai_status.get("capabilities", [])
            },
            "ai_status": ai_status
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"AI service error: {str(e)}",
            "timestamp": get_indian_time().isoformat()
        }

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity testing
    """
    return {
        "message": "pong",
        "timestamp": get_indian_time(),
        "status": "ok"
    }
