from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import AI service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
from ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Management"])

# Global AI service instance
ai_service_instance = None

async def get_ai_service():
    """Get or create AI service instance"""
    global ai_service_instance
    if ai_service_instance is None:
        ai_service_instance = AIService()
        await ai_service_instance.initialize()
    return ai_service_instance

@router.get("/status")
async def get_ai_status(ai_service: AIService = Depends(get_ai_service)):
    """
    Get comprehensive AI service status including Gemini integration
    """
    try:
        status = ai_service.get_status()
        
        # Add timestamp and additional information
        status["timestamp"] = datetime.now().isoformat()
        status["api_version"] = "v1"
        
        logger.info("AI status retrieved successfully")
        return status
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")

@router.get("/model-info")
async def get_ai_model_info(ai_service: AIService = Depends(get_ai_service)):
    """
    Get detailed AI model information
    """
    try:
        status = ai_service.get_status()
        
        # Extract model-specific information
        model_info = {
            "model_name": status.get("model_name", "Unknown"),
            "ai_models": status.get("ai_models", {}),
            "capabilities": status.get("capabilities", []),
            "status": status.get("status", "unknown"),
            "initialized": status.get("initialized", False),
            "timestamp": datetime.now().isoformat(),
        }
        
        logger.info("AI model info retrieved successfully")
        return model_info
    except Exception as e:
        logger.error(f"Error getting AI model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI model info: {str(e)}")

@router.post("/test")
async def test_ai_connection(
    test_data: Optional[Dict[str, Any]] = None,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Test AI connectivity and response quality
    """
    try:
        # Get test message from request or use default
        test_message = "Hello, this is a connectivity test."
        if test_data and "test_message" in test_data:
            test_message = test_data["test_message"]
        
        # Test AI chat functionality
        start_time = datetime.now()
        
        response = await ai_service.chat(
            message=test_message,
            session_id="test_session"
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Determine success based on response
        success = response and "response" in response and len(response["response"]) > 0
        
        result = {
            "success": success,
            "message": "AI test completed successfully" if success else "AI test failed",
            "test_message": test_message,
            "ai_response": response.get("response", "No response") if response else "No response",
            "processing_time": processing_time,
            "confidence": response.get("confidence", 0) if response else 0,
            "timestamp": datetime.now().isoformat(),
            "ai_service_status": ai_service.get_status(),
        }
        
        logger.info(f"AI test completed - Success: {success}, Time: {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error testing AI connection: {e}")
        result = {
            "success": False,
            "message": f"AI test failed: {str(e)}",
            "test_message": test_message if 'test_message' in locals() else "Unknown",
            "ai_response": None,
            "processing_time": 0,
            "confidence": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
        return result

@router.delete("/training-data")
async def clear_training_data(ai_service: AIService = Depends(get_ai_service)):
    """
    Clear all AI training data
    """
    try:
        result = ai_service.clear_training_data()
        
        # Add timestamp
        result["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Training data cleared: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error clearing training data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear training data: {str(e)}")

@router.get("/health")
async def get_ai_health():
    """
    Get basic AI service health status (lightweight check)
    """
    try:
        # Try to create AI service instance
        ai_service = AIService()
        
        # Basic initialization check
        basic_status = {
            "service": "AI Service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "gemini_library_available": True,  # Will be False if import fails
        }
        
        # Try to check if Gemini is available
        try:
            await ai_service.initialize()
            status = ai_service.get_status()
            basic_status["gemini_available"] = status.get("ai_models", {}).get("gemini_available", False)
            basic_status["model_name"] = status.get("model_name", "Unknown")
        except Exception as init_error:
            basic_status["status"] = "degraded"
            basic_status["gemini_available"] = False
            basic_status["initialization_error"] = str(init_error)
        
        return basic_status
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "service": "AI Service",
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "gemini_library_available": False,
            "gemini_available": False,
        }

@router.get("/capabilities")
async def get_ai_capabilities(ai_service: AIService = Depends(get_ai_service)):
    """
    Get AI service capabilities and features
    """
    try:
        status = ai_service.get_status()
        
        capabilities_info = {
            "capabilities": status.get("capabilities", []),
            "ai_models": status.get("ai_models", {}),
            "features": {
                "document_processing": True,
                "chat_interface": True,
                "training_data_management": True,
                "embeddings": status.get("embeddings_available", False),
                "advanced_search": status.get("sklearn_available", False),
            },
            "model_info": {
                "name": status.get("model_name", "Unknown"),
                "active_ai": status.get("ai_models", {}).get("active_ai", "Unknown"),
                "gemini_available": status.get("ai_models", {}).get("gemini_available", False),
            },
            "statistics": {
                "documents": status.get("document_count", 0),
                "chunks": status.get("total_chunks", 0),
                "knowledge_base_size_mb": status.get("knowledge_base_size_mb", 0),
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        return capabilities_info
        
    except Exception as e:
        logger.error(f"Error getting AI capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI capabilities: {str(e)}")
