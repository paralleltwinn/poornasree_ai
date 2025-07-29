from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
import os
import json
from datetime import datetime
import logging

# Import the enhanced service guide trainer
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_service_guide_trainer import EnhancedServiceGuideTrainer
except ImportError:
    # Fallback if the trainer is not available
    EnhancedServiceGuideTrainer = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Global trainer instance
service_trainer = None

def get_trainer():
    global service_trainer
    if service_trainer is None and EnhancedServiceGuideTrainer is not None:
        service_trainer = EnhancedServiceGuideTrainer()
    return service_trainer

@router.post("/train-service-guide")
async def train_service_guide_endpoint(
    file: UploadFile = File(...),
    user_id: str = "api_user"
):
    """Train Excel file as service guide with row-wise processing"""
    try:
        trainer = get_trainer()
        if trainer is None:
            raise HTTPException(
                status_code=500,
                detail="Service guide trainer not available"
            )
        
        # Validate file type (support both Excel and PDF)
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        supported_extensions = ['xlsx', 'xls', 'pdf']
        
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Only Excel files (.xlsx, .xls) and PDF files (.pdf) are supported for service guide training"
            )
        
        # Save uploaded file temporarily
        temp_file_path = f"temp_service_guide_{file.filename}"
        
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        try:
            # Train the service guide based on file type
            logger.info(f"Training service guide from file: {file.filename}")
            
            if file_extension in ['xlsx', 'xls']:
                result = await trainer.train_excel_service_guide(temp_file_path)
            elif file_extension == 'pdf':
                result = await trainer.train_pdf_service_guide(temp_file_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            if result["success"]:
                logger.info(f"Service guide training successful: {result.get('entries_trained', 0)} entries")
                
                # Return training results
                return JSONResponse(content={
                    "success": True,
                    "message": f"Service guide training completed successfully",
                    "entries_trained": result.get("entries_trained", 0),
                    "knowledge_base_entries": result.get("knowledge_base_entries", 0),
                    "file": file.filename,
                    "file_type": file_extension,
                    "training_summary": result.get("training_summary", {}),
                    "sample_entries": result.get("sample_entries", [])[:3],  # First 3 samples
                    "timestamp": datetime.now().isoformat()
                })
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Training failed: {result.get('error', 'Unknown error')}"
                )
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in service guide training: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during training: {str(e)}"
        )

@router.get("/entries")
async def get_service_guide_entries(
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    sheet: Optional[str] = Query(None, description="Filter by sheet"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries to return")
):
    """Get service guide entries with optional filtering"""
    try:
        # This would typically query a database
        # For now, return mock data or read from saved training results
        
        # Try to find recent training results
        training_files = []
        for file in os.listdir("."):
            if file.startswith("trained_service_guide_") and file.endswith(".json"):
                training_files.append(file)
        
        entries = []
        if training_files:
            # Load from most recent training file
            latest_file = max(training_files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                entries_data = json.load(f)
                
            # Convert to API format
            for entry_data in entries_data[:limit]:
                entry = {
                    "id": entry_data.get("id", ""),
                    "title": entry_data.get("title", ""),
                    "type": entry_data.get("type", "general"),
                    "category": entry_data.get("category", "general"),
                    "sheet": entry_data.get("sheet", ""),
                    "row": entry_data.get("row", 0),
                    "description": entry_data.get("description", ""),
                    "details": entry_data.get("details", ""),
                    "keywords": entry_data.get("keywords", []),
                    "searchable_content": entry_data.get("searchable_content", ""),
                    "raw_data": entry_data.get("raw_data", {}),
                    "created_at": datetime.now().isoformat()
                }
                
                # Apply filters
                if category and entry["category"].lower() != category.lower():
                    continue
                if type and entry["type"].lower() != type.lower():
                    continue
                if sheet and entry["sheet"].lower() != sheet.lower():
                    continue
                    
                entries.append(entry)
        
        return JSONResponse(content={
            "entries": entries,
            "total": len(entries),
            "filters": {
                "category": category,
                "type": type,
                "sheet": sheet
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting service guide entries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving entries: {str(e)}"
        )

@router.post("/search")
async def search_service_guide(
    request_data: dict
):
    """Search service guide entries"""
    try:
        query = request_data.get("query", "")
        limit = request_data.get("limit", 20)
        
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query is required"
            )
        
        # This would typically use the AI service for semantic search
        # For now, simple keyword matching from saved training results
        
        training_files = []
        for file in os.listdir("."):
            if file.startswith("trained_service_guide_") and file.endswith(".json"):
                training_files.append(file)
        
        results = []
        if training_files:
            latest_file = max(training_files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                entries_data = json.load(f)
            
            query_lower = query.lower()
            
            for entry_data in entries_data:
                # Simple keyword matching
                searchable_text = (
                    entry_data.get("title", "") + " " +
                    entry_data.get("description", "") + " " +
                    entry_data.get("searchable_content", "") + " " +
                    " ".join(entry_data.get("keywords", []))
                ).lower()
                
                if query_lower in searchable_text:
                    result = {
                        "id": entry_data.get("id", ""),
                        "title": entry_data.get("title", ""),
                        "type": entry_data.get("type", "general"),
                        "category": entry_data.get("category", "general"),
                        "sheet": entry_data.get("sheet", ""),
                        "row": entry_data.get("row", 0),
                        "description": entry_data.get("description", ""),
                        "details": entry_data.get("details", ""),
                        "keywords": entry_data.get("keywords", []),
                        "relevance_score": searchable_text.count(query_lower),
                        "created_at": datetime.now().isostring()
                    }
                    results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            results = results[:limit]
        
        return JSONResponse(content={
            "results": results,
            "query": query,
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching service guide: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )

@router.get("/stats")
async def get_service_guide_stats():
    """Get service guide statistics"""
    try:
        # Load statistics from training results
        training_files = []
        for file in os.listdir("."):
            if file.startswith("trained_service_guide_") and file.endswith(".json"):
                training_files.append(file)
        
        if not training_files:
            return JSONResponse(content={
                "total_entries": 0,
                "by_type": {},
                "by_category": {},
                "by_sheet": {},
                "last_updated": None,
                "message": "No service guide data available"
            })
        
        # Load from most recent training file
        latest_file = max(training_files, key=os.path.getctime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            entries_data = json.load(f)
        
        # Calculate statistics
        total_entries = len(entries_data)
        by_type = {}
        by_category = {}
        by_sheet = {}
        
        for entry in entries_data:
            # Count by type
            entry_type = entry.get("type", "unknown")
            by_type[entry_type] = by_type.get(entry_type, 0) + 1
            
            # Count by category
            category = entry.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1
            
            # Count by sheet
            sheet = entry.get("sheet", "unknown")
            by_sheet[sheet] = by_sheet.get(sheet, 0) + 1
        
        # Get file modification time
        last_updated = datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
        
        return JSONResponse(content={
            "total_entries": total_entries,
            "by_type": by_type,
            "by_category": by_category,
            "by_sheet": by_sheet,
            "last_updated": last_updated,
            "training_files": len(training_files),
            "latest_file": latest_file
        })
        
    except Exception as e:
        logger.error(f"Error getting service guide stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )
