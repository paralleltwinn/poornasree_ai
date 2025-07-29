from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from src.core.models.database_models import User, Document, ChatSession, ChatMessage as DBChatMessage, DocumentChunk, APIUsage
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    async def create_or_get_user(db: AsyncSession, user_id: str, name: str = None, email: str = None) -> User:
        """Create a new user or get existing user"""
        # Check if user exists
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                user_id=user_id,
                name=name,
                email=email
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    @staticmethod
    async def save_document(
        db: AsyncSession, 
        user_id: str, 
        filename: str, 
        file_type: str, 
        file_size: int, 
        file_path: str,
        description: str = None,
        chunk_count: int = None,
        processing_time: float = None,
        metadata: Dict = None,
        content_text: str = None
    ) -> Document:
        """Save document information to database"""
        document_id = str(uuid.uuid4())
        
        # Convert metadata dictionary to JSON string
        metadata_json = json.dumps(metadata) if metadata else None
        
        document = Document(
            document_id=document_id,
            user_id=user_id,
            filename=filename,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            description=description,
            chunk_count=chunk_count or 0,
            processing_time=processing_time,
            processing_status="completed",
            doc_metadata=metadata_json,
            content_text=content_text
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return document
    
    @staticmethod
    async def update_document_processing(
        db: AsyncSession, 
        document_id: str, 
        status: str, 
        content_text: str = None,
        chunk_count: int = None,
        processing_time: float = None
    ) -> Document:
        """Update document processing status"""
        result = await db.execute(select(Document).where(Document.document_id == document_id))
        document = result.scalar_one_or_none()
        
        if document:
            document.processing_status = status
            if content_text:
                document.content_text = content_text
            if chunk_count is not None:
                document.chunk_count = chunk_count
            if processing_time is not None:
                document.processing_time = processing_time
            
            await db.commit()
            await db.refresh(document)
        
        return document
    
    @staticmethod
    async def create_chat_session(db: AsyncSession, user_id: str, title: str = None) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    
    @staticmethod
    async def create_chat_session_with_id(db: AsyncSession, user_id: str, session_id: str, title: str = None) -> ChatSession:
        """Create a new chat session with specific ID"""
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    
    @staticmethod
    async def get_chat_session(db: AsyncSession, session_id: str) -> ChatSession:
        """Get chat session by ID"""
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def save_chat_message(
        db: AsyncSession,
        session_id: str,
        user_id: str,
        message_text: str,
        response_text: str = None,
        is_user_message: bool = True,
        confidence_score: float = None,
        processing_time: float = None,
        source_documents: List[Dict] = None
    ) -> DBChatMessage:
        """Save chat message to database"""
        message_id = str(uuid.uuid4())
        
        # Convert source_documents list to JSON string
        source_docs_json = json.dumps(source_documents) if source_documents else None
        
        message = DBChatMessage(
            message_id=message_id,
            session_id=session_id,
            user_id=user_id,
            message_text=message_text,
            response_text=response_text,
            is_user_message=is_user_message,
            confidence_score=confidence_score,
            processing_time=processing_time,
            source_documents=source_docs_json
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        return message
    
    @staticmethod
    async def get_user_chat_sessions(db: AsyncSession, user_id: str, limit: int = 20) -> List[ChatSession]:
        """Get user's chat sessions"""
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_chat_history(db: AsyncSession, session_id: str, limit: int = 100) -> List[DBChatMessage]:
        """Get chat history for a session"""
        result = await db.execute(
            select(DBChatMessage)
            .where(DBChatMessage.session_id == session_id)
            .order_by(DBChatMessage.created_at)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_document_stats(db: AsyncSession, user_id: str = None) -> Dict[str, Any]:
        """Get document statistics"""
        query = select(func.count(Document.id), func.sum(Document.file_size))
        
        if user_id:
            query = query.where(Document.user_id == user_id)
        
        result = await db.execute(query)
        count, total_size = result.first()
        
        # Get recent documents
        recent_query = select(Document).order_by(desc(Document.created_at)).limit(5)
        if user_id:
            recent_query = recent_query.where(Document.user_id == user_id)
        
        recent_result = await db.execute(recent_query)
        recent_docs = recent_result.scalars().all()
        
        return {
            "total_documents": count or 0,
            "total_size": total_size or 0,
            "recent_uploads": [
                {
                    "filename": doc.original_filename,
                    "size": doc.file_size,
                    "type": doc.file_type,
                    "upload_date": doc.created_at.isoformat(),
                    "status": doc.processing_status
                }
                for doc in recent_docs
            ]
        }
    
    @staticmethod
    async def log_api_usage(
        db: AsyncSession,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        processing_time: float = None,
        request_size: int = None,
        response_size: int = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> APIUsage:
        """Log API usage for monitoring"""
        usage = APIUsage(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            processing_time=processing_time,
            request_size=request_size,
            response_size=response_size,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        
        return usage
    
    @staticmethod
    async def get_system_stats(db: AsyncSession) -> Dict[str, Any]:
        """Get system statistics"""
        # Total users
        user_count = await db.execute(select(func.count(User.id)))
        total_users = user_count.scalar()
        
        # Total documents
        doc_count = await db.execute(select(func.count(Document.id)))
        total_documents = doc_count.scalar()
        
        # Total messages
        msg_count = await db.execute(select(func.count(DBChatMessage.id)))
        total_messages = msg_count.scalar()
        
        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(hours=24)
        
        recent_users = await db.execute(
            select(func.count(User.id)).where(User.created_at >= yesterday)
        )
        recent_docs = await db.execute(
            select(func.count(Document.id)).where(Document.created_at >= yesterday)
        )
        recent_messages = await db.execute(
            select(func.count(DBChatMessage.id)).where(DBChatMessage.created_at >= yesterday)
        )
        
        return {
            "total_users": total_users or 0,
            "total_documents": total_documents or 0,
            "total_messages": total_messages or 0,
            "recent_activity": {
                "new_users_24h": recent_users.scalar() or 0,
                "new_documents_24h": recent_docs.scalar() or 0,
                "new_messages_24h": recent_messages.scalar() or 0
            }
        }
    
    @staticmethod
    async def get_user_documents(
        db: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """Get documents for a specific user or all documents"""
        try:
            query = select(Document).order_by(Document.created_at.desc())
            
            if user_id:
                query = query.where(Document.user_id == user_id)
            
            query = query.offset(offset).limit(limit)
            
            result = await db.execute(query)
            documents = result.scalars().all()
            
            return list(documents)
            
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            return []

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: str) -> bool:
        """Delete a document and its associated chunks"""
        try:
            # First, delete associated document chunks
            chunks_result = await db.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )
            chunks = chunks_result.scalars().all()
            
            for chunk in chunks:
                await db.delete(chunk)
            
            # Then delete the document
            doc_result = await db.execute(
                select(Document).where(Document.document_id == document_id)
            )
            document = doc_result.scalar_one_or_none()
            
            if document:
                await db.delete(document)
                await db.commit()
                logger.info(f"Deleted document: {document.filename} ({document_id})")
                return True
            else:
                logger.warning(f"Document not found for deletion: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            await db.rollback()
            return False

    @staticmethod
    async def clear_all_documents(db: AsyncSession, user_id: str = None) -> Dict[str, Any]:
        """Clear all documents and their associated chunks. If user_id provided, only clear that user's documents."""
        try:
            deleted_count = 0
            
            # Get all documents (filtered by user if specified)
            if user_id:
                docs_result = await db.execute(
                    select(Document).where(Document.user_id == user_id)
                )
            else:
                docs_result = await db.execute(select(Document))
            
            documents = docs_result.scalars().all()
            
            for document in documents:
                # Delete associated document chunks first
                chunks_result = await db.execute(
                    select(DocumentChunk).where(DocumentChunk.document_id == document.document_id)
                )
                chunks = chunks_result.scalars().all()
                
                for chunk in chunks:
                    await db.delete(chunk)
                
                # Delete the document
                await db.delete(document)
                deleted_count += 1
                logger.info(f"Deleted document: {document.filename} ({document.document_id})")
            
            await db.commit()
            
            scope = f"for user {user_id}" if user_id else "for all users"
            logger.warning(f"Cleared all training data: {deleted_count} documents deleted {scope}")
            
            return {
                "deleted_count": deleted_count,
                "scope": "user" if user_id else "all",
                "user_id": user_id if user_id else None
            }
            
        except Exception as e:
            logger.error(f"Error clearing all documents: {e}")
            await db.rollback()
            raise e
