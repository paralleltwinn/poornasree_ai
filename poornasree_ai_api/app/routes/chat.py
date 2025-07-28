from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import time
from datetime import datetime
import logging
import pytz
from app.models import ChatMessage, ChatResponse, ErrorResponse
from app.services.ai_service import AIService
from app.services.database_service import DatabaseService
from app.database import get_database_session

logger = logging.getLogger(__name__)
router = APIRouter()

# Indian Standard Time timezone
IST = pytz.timezone('Asia/Kolkata')

def get_indian_time():
    """Get current time in Indian Standard Time"""
    return datetime.now(IST)

# Global AI service instance
ai_service = AIService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage, 
    db: AsyncSession = Depends(get_database_session)
):
    """
    Chat with the AI assistant about machine manuals
    
    - **message**: The user's question or message
    - **user_id**: Optional user identifier for session tracking
    - **session_id**: Optional session identifier for conversation history
    """
    try:
        start_time = time.time()
        
        # Ensure AI service is initialized
        if not ai_service.initialized:
            await ai_service.initialize()
        
        # Create or get user in database
        user = await DatabaseService.create_or_get_user(
            db, 
            message.user_id or "anonymous_user"
        )
        
        # Create chat session if not provided
        if not message.session_id:
            session = await DatabaseService.create_chat_session(
                db, 
                user.user_id,
                f"Chat {get_indian_time().strftime('%Y-%m-%d %H:%M')}"
            )
            session_id = session.session_id
        else:
            session_id = message.session_id
        
        # Generate AI response
        result = await ai_service.chat(
            message=message.message,
            session_id=session_id
        )
        
        processing_time = time.time() - start_time
        
        # Save user message to database
        await DatabaseService.save_chat_message(
            db,
            session_id=session_id,
            user_id=user.user_id,
            message_text=message.message,
            is_user_message=True
        )
        
        # Save AI response to database
        await DatabaseService.save_chat_message(
            db,
            session_id=session_id,
            user_id=user.user_id,
            message_text=message.message,
            response_text=result["response"],
            is_user_message=False,
            confidence_score=result.get("confidence"),
            processing_time=processing_time,
            source_documents=result.get("sources", [])
        )
        
        # Create response
        response = ChatResponse(
            response=result["response"],
            confidence=result.get("confidence"),
            sources=result.get("sources", []),
            timestamp=result.get("timestamp", get_indian_time()),
            processing_time=processing_time,
            session_id=session_id
        )
        
        logger.info(f"Chat response generated in {time.time() - start_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/chat/status")
async def get_chat_status():
    """
    Get the status of the chat service
    """
    try:
        status = ai_service.get_status()
        return {
            "service": "chat",
            "status": "healthy" if status["initialized"] else "initializing",
            "timestamp": get_indian_time(),
            **status
        }
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return {
            "service": "chat",
            "status": "error",
            "timestamp": get_indian_time(),
            "error": str(e)
        }

@router.post("/chat/feedback")
async def submit_feedback(feedback_data: dict):
    """
    Submit feedback about chat responses (for future improvements)
    """
    try:
        # Log feedback for analysis
        logger.info(f"User feedback received: {feedback_data}")
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "timestamp": get_indian_time()
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit feedback"
        )

@router.get("/chat/examples")
async def get_example_questions():
    """
    Get example questions users can ask
    """
    examples = [
        {
            "category": "Machine Operation",
            "questions": [
                "How do I start the machine?",
                "What is the proper startup sequence?",
                "How do I shut down the machine safely?",
                "What are the daily operation checks?"
            ]
        },
        {
            "category": "Troubleshooting",
            "questions": [
                "The machine won't start, what should I check?",
                "What does error code E001 mean?",
                "The machine is making unusual noises, what could be wrong?",
                "How do I reset the system after an error?"
            ]
        },
        {
            "category": "Maintenance",
            "questions": [
                "When should I perform routine maintenance?",
                "How do I clean the machine properly?",
                "What lubricants should I use?",
                "How often should I replace filters?"
            ]
        },
        {
            "category": "Safety",
            "questions": [
                "What safety precautions should I follow?",
                "What protective equipment is required?",
                "What are the emergency procedures?",
                "How do I handle hazardous materials safely?"
            ]
        }
    ]
    
    return {
        "examples": examples,
        "tip": "For best results, upload your machine manual first, then ask specific questions about your equipment."
    }
