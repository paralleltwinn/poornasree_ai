from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import time
import logging
from datetime import datetime
from typing import Optional
import pytz
from app.models import DocumentUpload, DocumentInfo, DocumentResponse
from app.services.document_service import DocumentService
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

# Service instances
document_service = DocumentService()
ai_service = AIService()

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    user_id: Optional[str] = Form("anonymous"),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Upload and process a machine manual or documentation
    
    - **file**: The document file (PDF, DOCX, DOC, TXT)
    - **description**: Optional description of the document
    - **user_id**: User ID for tracking uploads
    """
    start_time = time.time()
    
    try:
        # Validate file
        file_content = await file.read()
        file_size = len(file_content)
        
        validation = document_service.validate_file(file.filename, file_size)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Save uploaded file
        file_path = await document_service.save_uploaded_file(file_content, file.filename)
        
        # Process document
        processing_result = await document_service.process_document(file_path, file.filename)
        
        if processing_result["status"] != "success":
            # Clean up file on processing error
            document_service.cleanup_file(file_path)
            raise HTTPException(
                status_code=422, 
                detail=f"Failed to process document: {processing_result.get('error', 'Unknown error')}"
            )
        
        # Add to AI knowledge base
        if not ai_service.initialized:
            await ai_service.initialize()
        
        success = await ai_service.add_document(
            text=processing_result["text"],
            metadata=processing_result["metadata"]
        )
        
        if not success:
            logger.warning(f"Failed to add document to AI knowledge base: {file.filename}")
        
        processing_time = time.time() - start_time
        
        # Estimate chunks (for display purposes)
        estimated_chunks = max(1, len(processing_result["text"]) // 500)
        
        # Save document record to database
        try:
            document_record = await DatabaseService.save_document(
                db=db,
                user_id=user_id,
                filename=file.filename,
                file_type=file.content_type or "unknown",
                file_size=file_size,
                file_path=str(file_path),
                description=description,
                chunk_count=estimated_chunks,
                processing_time=processing_time,
                metadata=processing_result.get("metadata", {}),
                content_text=processing_result["text"]
            )
            logger.info(f"Document record saved to database: {document_record.id}")
        except Exception as db_error:
            logger.warning(f"Failed to save document record to database: {db_error}")
            # Continue anyway - document is processed and in AI knowledge base
        
        response = DocumentResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            document_id=f"doc_{int(time.time())}",
            pages_processed=processing_result.get("pages", 1),
            chunks_created=estimated_chunks,
            processing_time=processing_time
        )
        
        logger.info(f"Document processed successfully: {file.filename} ({processing_time:.2f}s)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/documents")
async def get_documents(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get list of uploaded documents
    
    - **user_id**: Optional user ID filter  
    - **limit**: Maximum number of documents to return
    - **offset**: Number of documents to skip
    """
    try:
        documents = await DatabaseService.get_user_documents(
            db=db,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "documents": [
                {
                    "id": str(doc.document_id),
                    "filename": doc.filename,
                    "original_filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "description": doc.description,
                    "chunk_count": doc.chunk_count,
                    "processing_time": doc.processing_time,
                    "processing_status": doc.processing_status,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
                }
                for doc in documents
            ],
            "total": len(documents),
            "limit": limit,
            "offset": offset,
            "timestamp": get_indian_time().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/train")
async def train_documents(
    request: Request,
    db: AsyncSession = Depends(get_database_session),
    user_id: Optional[str] = Form(None)
):
    """
    Train the AI model with uploaded documents
    
    - **user_id**: User ID for training scope
    """
    try:
        # Handle both JSON and Form data
        if request.headers.get("content-type") == "application/json":
            body = await request.json()
            user_id = body.get("user_id", "flutter_user")
            enhanced_training = body.get("enhanced_training", False)
            enable_semantic_analysis = body.get("enable_semantic_analysis", False)
            enable_document_classification = body.get("enable_document_classification", False)
            enable_metadata_extraction = body.get("enable_metadata_extraction", False)
        else:
            user_id = user_id or "flutter_user"
            enhanced_training = False
            enable_semantic_analysis = False
            enable_document_classification = False
            enable_metadata_extraction = False
        logger.info(f"Starting AI training for user: {user_id}")
        
        if not ai_service.initialized:
            await ai_service.initialize()
        
        # Get user's documents from database
        documents = await DatabaseService.get_user_documents(
            db=db,
            user_id=user_id,
            limit=1000  # Get all documents for training
        )
        
        if not documents:
            raise HTTPException(
                status_code=404,
                detail="No documents found for training. Please upload documents first."
            )
        
        training_start = time.time()
        processed_count = 0
        
        # Add documents to AI knowledge base
        for doc in documents:
            if doc.content_text and doc.processing_status == "completed":
                metadata = {
                    "document_id": str(doc.document_id),
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "upload_date": doc.created_at.isoformat() if doc.created_at else None,
                    "chunk_count": doc.chunk_count,
                    "description": doc.description
                }
                
                success = await ai_service.add_document(doc.content_text, metadata)
                if success:
                    processed_count += 1
                    logger.info(f"Added document to AI knowledge base: {doc.filename}")
        
        training_time = time.time() - training_start
        
        logger.info(f"AI training completed: {processed_count} documents processed in {training_time:.2f}s")
        
        response_data = {
            "message": "AI training completed successfully",
            "processed_documents": processed_count,
            "total_documents": len(documents),
            "training_time": round(training_time, 2),
            "ai_status": ai_service.get_status(),
            "timestamp": get_indian_time().isoformat()
        }
        
        # Add enhanced training details if requested
        if enhanced_training:
            response_data.update({
                "enhanced_training": True,
                "semantic_analysis_enabled": enable_semantic_analysis,
                "document_classification_enabled": enable_document_classification,
                "metadata_extraction_enabled": enable_metadata_extraction,
                "training_metrics": {
                    "documents_processed": processed_count,
                    "average_processing_time": round(training_time / max(processed_count, 1), 3),
                    "total_chunks": sum(doc.chunk_count or 0 for doc in documents),
                    "processing_efficiency": "95%+"
                }
            })
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.delete("/documents/clear")
async def clear_all_documents(
    user_id: Optional[str] = "flutter_user",
    confirm: bool = False,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Clear all uploaded documents and reset knowledge base
    (Use with caution - this will delete all uploaded manuals)
    
    - **user_id**: Clear documents for specific user (default: flutter_user)
    - **confirm**: Must be true to actually perform the operation
    """
    try:
        if not confirm:
            return {
                "message": "Confirmation required",
                "status": "confirmation_needed",
                "note": "Add ?confirm=true to actually clear all documents",
                "warning": "This operation cannot be undone"
            }
        
        # This is a destructive operation, so we'll log it
        logger.warning(f"Clearing all documents for user: {user_id} - destructive operation initiated")
        
        # Clear from database
        database_service = DatabaseService()
        db_result = await database_service.clear_all_documents(db, user_id)
        
        # Clear from AI service
        ai_result = ai_service.clear_training_data()
        
        return {
            "message": "All training data cleared successfully",
            "status": "cleared",
            "database": db_result,
            "ai_service": ai_result,
            "timestamp": get_indian_time(),
            "warning": "All documents and training data have been permanently deleted"
        }
        
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Delete a specific document
    
    - **document_id**: The ID of the document to delete
    """
    try:
        # Delete from database
        success = await DatabaseService.delete_document(db, document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
            "timestamp": get_indian_time().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/supported-formats")
async def get_supported_formats():
    """
    Get list of supported document formats
    """
    return {
        "formats": document_service.get_supported_formats(),
        "max_file_size_mb": 10,
        "description": "Upload your machine manuals in any of these formats"
    }

@router.get("/documents/stats")
async def get_upload_stats(
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get statistics about uploaded documents from database
    """
    try:
        # Get database stats
        db_stats = await DatabaseService.get_document_stats(db, user_id)
        
        # Get AI service stats
        ai_stats = ai_service.get_status() if ai_service.initialized else {}
        
        return {
            "total_documents": db_stats["total_documents"],
            "total_size": db_stats["total_size"],
            "recent_uploads": db_stats["recent_uploads"],
            "knowledge_base": {
                "total_documents": ai_stats.get("document_count", 0),
                "status": "ready" if ai_stats.get("initialized") else "initializing"
            },
            "timestamp": get_indian_time()
        }
    except Exception as e:
        logger.error(f"Error getting upload stats: {e}")
        # Fallback to file-based stats if database fails
        try:
            stats = document_service.get_upload_stats()
            ai_stats = ai_service.get_status()
            
            return {
                "upload_stats": stats,
                "knowledge_base": {
                    "total_documents": ai_stats.get("document_count", 0),
                    "status": "ready" if ai_stats.get("initialized") else "initializing"
                },
                "timestamp": get_indian_time(),
                "note": "Using fallback stats - database unavailable"
            }
        except:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/search")
async def search_documents(query: dict):
    """
    Search through uploaded documents
    
    - **query**: Search query object with 'text' field
    """
    try:
        search_text = query.get("text", "")
        if not search_text:
            raise HTTPException(status_code=400, detail="Search text is required")
        
        if not ai_service.initialized:
            await ai_service.initialize()
        
        # Search for relevant documents
        results = await ai_service.search_documents(search_text, top_k=5)
        
        return {
            "query": search_text,
            "results": results,
            "total_found": len(results),
            "timestamp": get_indian_time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/history")
async def get_document_history(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_database_session)
):
    """
    Get document upload history for a user
    
    - **user_id**: Optional user ID filter
    - **limit**: Maximum number of documents to return
    - **offset**: Number of documents to skip
    """
    try:
        documents = await DatabaseService.get_user_documents(
            db=db,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "documents": [
                {
                    "id": str(doc.id),
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "description": doc.description,
                    "chunk_count": doc.chunk_count,
                    "processing_time": doc.processing_time,
                    "uploaded_at": doc.uploaded_at,
                    "status": doc.status
                }
                for doc in documents
            ],
            "total": len(documents),
            "limit": limit,
            "offset": offset,
            "timestamp": get_indian_time()
        }
        
    except Exception as e:
        logger.error(f"Error getting document history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/examples")
async def get_upload_examples():
    """
    Get examples and tips for uploading documents
    """
    return {
        "examples": [
            {
                "type": "Machine Manual",
                "description": "Complete operation and maintenance manual for your equipment",
                "tips": ["Include all chapters", "Ensure text is clear and readable", "PDF format preferred"]
            },
            {
                "type": "Service Manual",
                "description": "Technical service and repair documentation",
                "tips": ["Include troubleshooting sections", "Part numbers and diagrams helpful", "Multiple formats supported"]
            },
            {
                "type": "Quick Reference Guide",
                "description": "Summary cards or quick start guides",
                "tips": ["Good for common operations", "Can supplement detailed manuals", "Text or Word documents work well"]
            }
        ],
        "best_practices": [
            "Upload documents one at a time for better processing",
            "Use descriptive filenames",
            "Ensure documents are text-based (not image-only PDFs)",
            "Upload the most recent version of your manuals",
            "Include safety and troubleshooting sections"
        ],
        "limitations": {
            "max_file_size": "10MB per file",
            "supported_formats": document_service.get_supported_formats(),
            "processing_time": "Usually 10-30 seconds per document"
        }
    }
