import os
import time
import re
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pickle

# Import for embeddings (fallback to simple if not available)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using basic keyword matching.")

# Import for vector similarity
try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using basic similarity.")

logger = logging.getLogger(__name__)

class AIService:
    """Production-ready AI service with advanced document processing and retrieval"""
    
    def __init__(self):
        self.initialized = False
        self.documents = []  # Document storage with embeddings
        self.embeddings = []  # Vector embeddings for documents
        self.model_name = "poornasree-ai-v2.0"
        self.embedding_model = None
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 50  # Overlap between chunks
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.knowledge_base_path = "./data/knowledge_base.pkl"
        self._ensure_data_directory()
        self.knowledge_base_path = "./data/knowledge_base.pkl"
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        """Create data directory for knowledge base storage"""
        os.makedirs("./data", exist_ok=True)
        
    async def initialize(self):
        """Initialize the AI service with advanced capabilities"""
        try:
            logger.info("Initializing Poornasree AI service v2.0...")
            
            # Initialize embedding model if available
            if EMBEDDINGS_AVAILABLE:
                try:
                    loop = asyncio.get_event_loop()
                    self.embedding_model = await loop.run_in_executor(
                        self.executor, 
                        lambda: SentenceTransformer('all-MiniLM-L6-v2')
                    )
                    logger.info("✅ Sentence transformer model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load embedding model: {e}")
                    self.embedding_model = None
            
            # Load existing knowledge base
            await self._load_knowledge_base()
            
            self.initialized = True
            logger.info("✅ Poornasree AI service v2.0 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.initialized = False
            return False
    
    async def _load_knowledge_base(self):
        """Load existing knowledge base from disk"""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = data.get('embeddings', [])
                logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            logger.warning(f"Failed to load knowledge base: {e}")
            self.documents = []
            self.embeddings = []
    
    async def _save_knowledge_base(self):
        """Save knowledge base to disk"""
        try:
            data = {
                'documents': self.documents,
                'embeddings': self.embeddings,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.knowledge_base_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks for better retrieval"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for paragraph breaks
                    para_end = text.rfind('\n', start, end)
                    if para_end > start + self.chunk_size // 2:
                        end = para_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def get_status(self) -> dict:
        """Get current AI service status"""
        return {
            "initialized": self.initialized,
            "model_name": self.model_name,
            "documents_count": len(self.documents),
            "embeddings_available": EMBEDDINGS_AVAILABLE and self.embedding_model is not None,
            "total_chunks": sum(len(doc.get('chunks', [])) for doc in self.documents),
            "knowledge_base_size_mb": self._get_knowledge_base_size(),
            "status": "ready" if self.initialized else "not_initialized"
        }
    
    def _get_knowledge_base_size(self) -> float:
        """Get knowledge base file size in MB"""
        try:
            if os.path.exists(self.knowledge_base_path):
                size_bytes = os.path.getsize(self.knowledge_base_path)
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except:
            return 0.0
    
    async def add_document(self, text: str, metadata: dict) -> bool:
        """Add document to knowledge base with advanced processing"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Validate text content
            if not text or len(text.strip()) < 10:
                logger.warning(f"Skipping document with insufficient content: {metadata.get('filename', 'unknown')}")
                return False
            
            filename = metadata.get('filename', 'unknown')
            
            # Check for duplicates
            for existing_doc in self.documents:
                if existing_doc.get('metadata', {}).get('filename') == filename:
                    logger.info(f"Document already exists, updating: {filename}")
                    # Remove existing document and its embeddings
                    doc_index = self.documents.index(existing_doc)
                    self.documents.pop(doc_index)
                    if doc_index < len(self.embeddings):
                        self.embeddings.pop(doc_index)
                    break
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Split into chunks for better retrieval
            chunks = self._chunk_text(cleaned_text)
            
            # Generate embeddings if model is available
            chunk_embeddings = []
            if self.embedding_model is not None:
                try:
                    loop = asyncio.get_event_loop()
                    chunk_embeddings = await loop.run_in_executor(
                        self.executor,
                        lambda: self.embedding_model.encode(chunks).tolist()
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate embeddings: {e}")
                    chunk_embeddings = []
            
            # Create document entry
            doc_entry = {
                "text": cleaned_text,
                "chunks": chunks,
                "metadata": {
                    **metadata,
                    "word_count": len(cleaned_text.split()),
                    "char_count": len(cleaned_text),
                    "chunk_count": len(chunks),
                    "processed_at": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat(),
                "id": len(self.documents) + 1,
                "embeddings": chunk_embeddings
            }
            
            self.documents.append(doc_entry)
            
            # Save to persistent storage
            await self._save_knowledge_base()
            
            logger.info(f"Document processed successfully: {filename} ({len(chunks)} chunks, {len(cleaned_text.split())} words)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better AI processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\"\'\/]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        # Remove very short lines (likely artifacts)
        lines = text.split('\n')
        lines = [line.strip() for line in lines if len(line.strip()) > 3]
        
        return '\n'.join(lines).strip()

    async def train_from_documents(self, documents_data: List[Dict]) -> Dict:
        """Train the AI with multiple documents"""
        try:
            if not self.initialized:
                await self.initialize()
            
            processed_count = 0
            failed_count = 0
            total_words = 0
            
            for doc_data in documents_data:
                text = doc_data.get('content_text', '')
                metadata = doc_data.get('metadata', {})
                
                if await self.add_document(text, metadata):
                    processed_count += 1
                    total_words += len(text.split())
                else:
                    failed_count += 1
            
            return {
                "processed_documents": processed_count,
                "failed_documents": failed_count,
                "total_documents_in_kb": len(self.documents),
                "total_words": total_words,
                "status": "success" if processed_count > 0 else "failed"
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                "processed_documents": 0,
                "failed_documents": len(documents_data),
                "status": "error",
                "error": str(e)
            }
    
    async def chat(self, message: str, session_id: str = None) -> Dict:
        """Process chat message with advanced document retrieval"""
        try:
            if not self.initialized:
                await self.initialize()
            
            start_time = time.time()
            
            # Search for relevant documents
            relevant_docs = await self.search_documents(message, top_k=5)
            
            # Generate context-aware response
            response_text = await self._generate_intelligent_response(message, relevant_docs)
            
            # Calculate confidence based on document matches
            confidence = self._calculate_confidence(message, relevant_docs)
            
            processing_time = time.time() - start_time
            
            return {
                "response": response_text,
                "confidence": confidence,
                "source_documents": [
                    {
                        "filename": doc["metadata"].get("filename", "unknown"),
                        "score": doc["score"],
                        "snippet": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
                    }
                    for doc in relevant_docs[:3]  # Top 3 sources
                ],
                "processing_time": round(processing_time, 2),
                "session_id": session_id or "default",
                "documents_searched": len(self.documents),
                "chunks_analyzed": sum(len(doc.get('chunks', [])) for doc in self.documents)
            }
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "confidence": 0.0,
                "source_documents": [],
                "processing_time": 0.0,
                "session_id": session_id or "default"
            }
    
    async def _generate_intelligent_response(self, message: str, relevant_docs: List[Dict]) -> str:
        """Generate intelligent response based on message and relevant documents"""
        message_lower = message.lower()
        
        # If we have relevant documents, use them to answer
        if relevant_docs and len(relevant_docs) > 0:
            # Extract key information from top documents
            context_info = []
            for doc in relevant_docs[:3]:
                context_info.append({
                    "text": doc["text"],
                    "filename": doc["metadata"].get("filename", "unknown"),
                    "score": doc["score"]
                })
            
            # Generate response based on context
            if any(word in message_lower for word in ["how", "what", "where", "when", "why"]):
                return self._generate_instructional_response(message, context_info)
            elif any(word in message_lower for word in ["troubleshoot", "problem", "issue", "error", "fault"]):
                return self._generate_troubleshooting_response(message, context_info)
            elif any(word in message_lower for word in ["safety", "danger", "hazard", "risk"]):
                return self._generate_safety_response(message, context_info)
            elif any(word in message_lower for word in ["maintenance", "service", "repair"]):
                return self._generate_maintenance_response(message, context_info)
            else:
                return self._generate_general_response(message, context_info)
        
        # Fallback to general AI responses if no relevant documents
        return self._generate_fallback_response(message)
    
    def _generate_instructional_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate step-by-step instructional response"""
        best_match = context_info[0] if context_info else None
        if not best_match:
            return "I don't have specific information about that in the uploaded manuals. Could you provide more details or check if the relevant manual has been uploaded?"
        
        response = f"Based on the information from '{best_match['filename']}', here's what I found:\n\n"
        
        # Extract relevant text
        text = best_match['text']
        
        # Look for numbered steps or bullet points
        if any(pattern in text.lower() for pattern in ['step', '1.', '2.', 'first', 'then', 'next']):
            response += "**Procedure:**\n"
            response += self._extract_procedure_steps(text)
        else:
            response += self._extract_relevant_information(text, message)
        
        # Add source information
        response += f"\n\n*Source: {best_match['filename']} (Relevance: {best_match['score']:.0%})*"
        
        if len(context_info) > 1:
            response += f"\n\nI also found related information in {len(context_info)-1} other document(s). Would you like me to provide additional details?"
        
        return response
    
    def _generate_troubleshooting_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate troubleshooting response"""
        response = "**Troubleshooting Guide:**\n\n"
        
        for i, doc in enumerate(context_info[:2]):
            text = doc['text'].lower()
            
            # Look for troubleshooting keywords
            if any(word in text for word in ['problem', 'issue', 'error', 'fault', 'check', 'verify']):
                response += f"**From {doc['filename']}:**\n"
                response += self._extract_troubleshooting_steps(doc['text'])
                response += "\n\n"
        
        response += "**Additional Steps:**\n"
        response += "1. Check all connections and power supply\n"
        response += "2. Verify all safety systems are functioning\n"
        response += "3. Consult the error code manual if available\n"
        response += "4. Contact technical support if the issue persists\n"
        
        return response
    
    def _generate_safety_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate safety-focused response"""
        response = "⚠️ **SAFETY INFORMATION** ⚠️\n\n"
        
        for doc in context_info[:2]:
            text = doc['text'].lower()
            if any(word in text for word in ['safety', 'warning', 'caution', 'danger', 'hazard']):
                response += f"**From {doc['filename']}:**\n"
                response += self._extract_safety_information(doc['text'])
                response += "\n\n"
        
        response += "**General Safety Reminders:**\n"
        response += "• Always follow lockout/tagout procedures\n"
        response += "• Wear appropriate personal protective equipment (PPE)\n"
        response += "• Ensure emergency stops are accessible and functional\n"
        response += "• Never bypass safety systems\n"
        
        return response
    
    def _generate_maintenance_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate maintenance-focused response"""
        response = "🔧 **Maintenance Information:**\n\n"
        
        for doc in context_info[:2]:
            text = doc['text'].lower()
            if any(word in text for word in ['maintenance', 'service', 'lubrication', 'inspection']):
                response += f"**From {doc['filename']}:**\n"
                response += self._extract_maintenance_procedures(doc['text'])
                response += "\n\n"
        
        response += "**General Maintenance Tips:**\n"
        response += "• Follow the recommended maintenance schedule\n"
        response += "• Use only approved parts and lubricants\n"
        response += "• Keep detailed maintenance records\n"
        response += "• Perform regular inspections\n"
        
        return response
    
    def _generate_general_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate general response with context"""
        best_match = context_info[0] if context_info else None
        if not best_match:
            return "I don't have specific information about that in the uploaded manuals. Could you provide more details?"
        
        response = f"Based on the information from '{best_match['filename']}':\n\n"
        response += self._extract_relevant_information(best_match['text'], message)
        response += f"\n\n*Source: {best_match['filename']}*"
        
        return response
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when no documents match"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm Poornasree AI, your technical documentation assistant. I can help you with machine manuals, troubleshooting, maintenance procedures, and safety information. Upload your manuals to get started, or ask me about any technical topics!"
        
        return f"I understand you're asking about '{message}', but I don't have specific information about this in the currently uploaded manuals. To get the most accurate help:\n\n1. Upload relevant technical manuals or documentation\n2. Use the 'Train AI Model' feature to process them\n3. Ask specific questions about your equipment\n\nI can help with operation procedures, troubleshooting, maintenance, safety protocols, and technical specifications once the relevant documentation is uploaded."
    
    def _extract_procedure_steps(self, text: str) -> str:
        """Extract step-by-step procedures from text"""
        lines = text.split('\n')
        procedure_lines = []
        
        for line in lines:
            line = line.strip()
            if any(pattern in line.lower() for pattern in ['step', '1.', '2.', '3.', '4.', '5.']):
                procedure_lines.append(f"• {line}")
            elif line and len(procedure_lines) > 0 and len(line) > 10:
                procedure_lines.append(f"  {line}")
        
        return '\n'.join(procedure_lines[:10])  # Limit to 10 steps
    
    def _extract_relevant_information(self, text: str, query: str) -> str:
        """Extract most relevant information from text based on query"""
        query_words = query.lower().split()
        sentences = text.split('.')
        
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                score = sum(1 for word in query_words if word in sentence.lower())
                if score > 0:
                    scored_sentences.append((sentence, score))
        
        # Sort by relevance and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored_sentences[:3]]
        
        return '. '.join(top_sentences) + '.' if top_sentences else text[:500] + "..."
    
    def _extract_troubleshooting_steps(self, text: str) -> str:
        """Extract troubleshooting steps from text"""
        lines = text.split('\n')
        troubleshooting_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['check', 'verify', 'ensure', 'test', 'inspect', 'if']):
                if len(line) > 10:
                    troubleshooting_lines.append(f"• {line}")
        
        return '\n'.join(troubleshooting_lines[:8])  # Limit to 8 steps
    
    def _extract_safety_information(self, text: str) -> str:
        """Extract safety information from text"""
        lines = text.split('\n')
        safety_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['warning', 'caution', 'danger', 'safety', 'never', 'always', 'must']):
                if len(line) > 10:
                    safety_lines.append(f"⚠️ {line}")
        
        return '\n'.join(safety_lines[:6])  # Limit to 6 safety points
    
    def _extract_maintenance_procedures(self, text: str) -> str:
        """Extract maintenance procedures from text"""
        lines = text.split('\n')
        maintenance_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['lubricate', 'clean', 'replace', 'inspect', 'service', 'check']):
                if len(line) > 10:
                    maintenance_lines.append(f"🔧 {line}")
        
        return '\n'.join(maintenance_lines[:8])  # Limit to 8 maintenance items
    
    def _calculate_confidence(self, message: str, relevant_docs: List[Dict]) -> float:
        """Calculate confidence score based on document matches"""
        if not relevant_docs:
            return 0.1
        
        # Base confidence on top document score
        top_score = relevant_docs[0]["score"] if relevant_docs else 0
        
        # Boost confidence if multiple documents match
        doc_count_bonus = min(len(relevant_docs) * 0.1, 0.3)
        
        # Boost confidence for specific question types
        message_lower = message.lower()
        question_bonus = 0.1 if any(word in message_lower for word in ["how", "what", "where"]) else 0
        
        final_confidence = min(top_score + doc_count_bonus + question_bonus, 0.95)
        return round(final_confidence, 2)
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Advanced document search with embeddings and keyword matching"""
        try:
            if not self.documents:
                return []
            
            results = []
            
            # Use embeddings if available
            if self.embedding_model is not None and SKLEARN_AVAILABLE:
                results = await self._embedding_search(query, top_k)
            else:
                results = await self._keyword_search(query, top_k)
            
            return results
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
    
    async def _embedding_search(self, query: str, top_k: int) -> List[Dict]:
        """Search using sentence embeddings for better semantic matching"""
        try:
            # Generate query embedding
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                self.executor,
                lambda: self.embedding_model.encode([query])
            )
            
            all_results = []
            
            for doc in self.documents:
                if not doc.get('embeddings'):
                    continue
                
                chunks = doc.get('chunks', [])
                chunk_embeddings = doc['embeddings']
                
                if len(chunks) != len(chunk_embeddings):
                    continue
                
                # Calculate similarity for each chunk
                similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
                
                for i, (chunk, similarity) in enumerate(zip(chunks, similarities)):
                    if similarity > 0.1:  # Threshold for relevance
                        all_results.append({
                            "text": chunk,
                            "metadata": doc["metadata"],
                            "score": float(similarity),
                            "document_id": doc["id"],
                            "chunk_id": i
                        })
            
            # Sort by similarity score
            all_results.sort(key=lambda x: x["score"], reverse=True)
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"Embedding search failed: {e}")
            return await self._keyword_search(query, top_k)
    
    async def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Fallback keyword-based search with improved scoring"""
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            chunks = doc.get('chunks', [doc['text']])
            
            for i, chunk in enumerate(chunks):
                chunk_lower = chunk.lower()
                
                # Calculate different types of matches
                exact_matches = sum(1 for word in query_words if word in chunk_lower)
                partial_matches = sum(1 for word in query_words 
                                    if any(word in chunk_word for chunk_word in chunk_lower.split()))
                
                # Boost score for exact phrase matches
                phrase_bonus = 0.5 if query.lower() in chunk_lower else 0
                
                # Calculate final score
                total_score = (exact_matches * 2 + partial_matches + phrase_bonus) / (len(query_words) + 1)
                
                if total_score > 0.1:
                    results.append({
                        "text": chunk,
                        "metadata": doc["metadata"],
                        "score": total_score,
                        "document_id": doc["id"],
                        "chunk_id": i,
                        "exact_matches": exact_matches,
                        "partial_matches": partial_matches
                    })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_status(self) -> Dict:
        """Get AI service status with detailed information"""
        return {
            "initialized": self.initialized,
            "model_name": self.model_name,
            "document_count": len(self.documents),
            "total_chunks": sum(len(doc.get('chunks', [])) for doc in self.documents),
            "embeddings_available": EMBEDDINGS_AVAILABLE and self.embedding_model is not None,
            "sklearn_available": SKLEARN_AVAILABLE,
            "knowledge_base_size_mb": self._get_knowledge_base_size(),
            "mode": "advanced_ai" if self.embedding_model else "keyword_ai",
            "status": "ready" if self.initialized else "not_initialized",
            "capabilities": [
                "Advanced Document Search",
                "Context-Aware Responses", 
                "Technical Troubleshooting",
                "Maintenance Guidance",
                "Safety Information",
                "Procedure Extraction",
                "Multi-Document Analysis"
            ]
        }
    
    def cleanup(self):
        """Cleanup resources and save state"""
        try:
            # Save knowledge base before cleanup
            if self.documents:
                asyncio.create_task(self._save_knowledge_base())
            
            self.documents.clear()
            self.embeddings.clear()
            self.initialized = False
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("AI service cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def clear_training_data(self) -> Dict:
        """Clear all training data from AI service"""
        try:
            document_count = len(self.documents)
            chunk_count = sum(len(doc.get('chunks', [])) for doc in self.documents)
            
            self.documents.clear()
            self.embeddings.clear()
            
            # Remove knowledge base file
            if os.path.exists(self.knowledge_base_path):
                os.remove(self.knowledge_base_path)
            
            logger.warning(f"Cleared {document_count} documents ({chunk_count} chunks) from AI training data")
            
            return {
                "message": "Training data cleared successfully",
                "cleared_documents": document_count,
                "cleared_chunks": chunk_count,
                "status": "cleared",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error clearing training data: {e}")
            raise e
