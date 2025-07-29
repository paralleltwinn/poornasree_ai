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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Import for Google Gemini AI integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Gemini integration disabled.")

logger = logging.getLogger(__name__)

class AIService:
    """Production-ready AI service with advanced document processing and retrieval"""
    
    def __init__(self):
        self.initialized = False
        self.documents = []  # Document storage with embeddings
        self.embeddings = []  # Vector embeddings for documents
        self.model_name = "poornasree-ai-v3.0-gemini"
        self.embedding_model = None
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 50  # Overlap between chunks
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.knowledge_base_path = "./data/knowledge_base.pkl"
        self._ensure_data_directory()
        
        # Google Gemini configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = "gemini-2.5-flash-lite"  # Use gemini-2.5-flash-lite entirely
        self.gemini_available = False
        self.gemini_client = None
        
    def _ensure_data_directory(self):
        """Create data directory for knowledge base storage"""
        os.makedirs("./data", exist_ok=True)
    
    async def _initialize_gemini(self):
        """Initialize Google Gemini AI connection"""
        # Initialize as False first
        self.gemini_available = False
        
        try:
            if not GEMINI_AVAILABLE:
                logger.info("🤖 Gemini: google-generativeai library not available, skipping Gemini initialization")
                return
            
            if not self.gemini_api_key:
                logger.info("🤖 Gemini: API key not provided, skipping Gemini initialization")
                return
            
            # Configure Gemini AI
            genai.configure(api_key=self.gemini_api_key)
            
            # Initialize the model
            self.gemini_client = genai.GenerativeModel(self.gemini_model)
            
            # Test connection with a simple request
            test_response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content("Hello, test connection")
            )
            
            if test_response and test_response.text:
                self.gemini_available = True
                logger.info(f"🚀 Gemini connected successfully! Using model: {self.gemini_model}")
                logger.info("🚀 Gemini is now the primary AI model for enhanced responses")
            else:
                logger.warning("🤖 Gemini test failed, falling back to local models")
                self.gemini_available = False
                
        except Exception as e:
            logger.warning(f"🤖 Gemini initialization failed: {e}")
            logger.info("🤖 Will use local fallback models")
            self.gemini_available = False
    
    async def _query_gemini(self, prompt: str, max_tokens: int = 800) -> str:
        """Query Google Gemini model with a prompt"""
        try:
            if not self.gemini_available or not self.gemini_client:
                return None
            
            # Prepare the enhanced prompt for Gemini 2.5 Flash-Lite
            enhanced_prompt = f"""You are Poornasree AI, a technical documentation assistant powered by Google Gemini 2.5 Flash-Lite. Provide clear, accurate, and helpful responses based on the provided context. Focus on safety, procedures, and technical accuracy.

User Query: {prompt}

Please provide a comprehensive and helpful response."""
            
            # Make the API call to Gemini
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(
                    enhanced_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                        top_p=0.9,
                    )
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return None
                
        except Exception as e:
            logger.warning(f"Gemini query failed: {e}")
            return None
        
    async def initialize(self):
        """Initialize the AI service with advanced capabilities"""
        try:
            logger.info("Initializing Poornasree AI service v3.0 with Google Gemini integration...")
            
            # Initialize Gemini connection
            await self._initialize_gemini()
            
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
            
            # Log AI model status
            if self.gemini_available:
                logger.info("✅ Poornasree AI service v3.0 initialized with Google Gemini integration!")
                logger.info("🚀 Using Gemini for enhanced AI responses")
            else:
                logger.info("✅ Poornasree AI service v3.0 initialized with local processing")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.initialized = False
            return False
    
    def get_ai_status(self):
        """Get detailed AI service status for debugging"""
        return {
            "initialized": self.initialized,
            "gemini_available": self.gemini_available,
            "gemini_api_key_present": bool(self.gemini_api_key),
            "gemini_library_available": GEMINI_AVAILABLE,
            "gemini_model": self.gemini_model,
            "embedding_model_available": self.embedding_model is not None,
            "documents_count": len(self.documents) if hasattr(self, 'documents') else 0
        }
    
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
        """Process chat message with advanced document retrieval and Gemini AI entirely"""
        try:
            if not self.initialized:
                await self.initialize()
            
            start_time = time.time()
            
            # Search for relevant documents
            relevant_docs = await self.search_documents(message, top_k=5)
            
            # Generate response using Gemini 2.5 Flash-Lite entirely
            if self.gemini_available:
                response_text = await self._generate_gemini_comprehensive_response(message, relevant_docs)
                if not response_text:
                    # If Gemini fails, use structured fallback
                    response_text = await self._generate_intelligent_response(message, relevant_docs)
                ai_model_used = "Google Gemini 2.5 Flash-Lite"
            else:
                # Use structured response if Gemini not available
                response_text = await self._generate_intelligent_response(message, relevant_docs)
                ai_model_used = "Local Processing"
            
            # Calculate confidence based on document matches and AI model
            confidence = self._calculate_enhanced_confidence(message, relevant_docs)
            
            processing_time = time.time() - start_time
            
            return {
                "response": response_text,
                "confidence": confidence,
                "ai_used": ai_model_used,
                "model_used": "Gemini 2.5 Flash-Lite" if self.gemini_available else "Local Model",
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
                "chunks_analyzed": sum(len(doc.get('chunks', [])) for doc in self.documents),
                "gemini_status": "active" if self.gemini_available else "unavailable"
            }
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "confidence": 0.0,
                "ai_used": "Error Handler",
                "model_used": "Fallback",
                "source_documents": [],
                "processing_time": 0.0,
                "session_id": session_id or "default"
            }
    
    async def _generate_intelligent_response(self, message: str, relevant_docs: List[Dict]) -> str:
        """Generate focused response based on message and relevant documents"""
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
            
            # Generate focused response based on the specific question
            return await self._generate_focused_response(message, context_info)
        
        # Fallback to general AI responses if no relevant documents
        return self._generate_fallback_response(message)

    async def _generate_gemini_comprehensive_response(self, message: str, relevant_docs: List[Dict]) -> str:
        """Generate comprehensive response using Gemini AI with full context"""
        try:
            if not self.gemini_available or not self.gemini_client:
                return None
            
            # Prepare comprehensive context
            if relevant_docs and len(relevant_docs) > 0:
                # Use document-based response
                context_info = []
                for doc in relevant_docs[:3]:
                    context_info.append({
                        "text": doc["text"],
                        "filename": doc["metadata"].get("filename", "unknown"),
                        "score": doc["score"]
                    })
                return await self._generate_gemini_enhanced_response(message, context_info)
            else:
                # Use fallback response
                return await self._generate_gemini_fallback_response(message)
                
        except Exception as e:
            logger.warning(f"Gemini comprehensive response failed: {e}")
            return None
    
    async def _generate_focused_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate focused response that directly answers the specific question using Gemini AI entirely"""
        best_match = context_info[0] if context_info else None
        if not best_match:
            # Use Gemini for fallback responses too
            if self.gemini_available:
                fallback_response = await self._generate_gemini_fallback_response(message)
                if fallback_response:
                    return fallback_response
            return f"I don't have specific information about '{message}' in the uploaded manuals. Please upload the relevant documentation to get accurate answers."
        
        message_lower = message.lower()
        
        # Prioritize Gemini for ALL responses
        try:
            ai_response = await self._generate_gemini_enhanced_response(message, context_info)
            if ai_response:
                logger.info("✅ Using Gemini AI for enhanced response generation")
                return ai_response
        except Exception as e:
            logger.warning(f"Gemini enhancement failed, using structured fallback: {e}")
        
        # Only use structured fallback if Gemini completely fails
        relevant_text = self._extract_relevant_information(best_match['text'], message)
        
        # Create a direct, focused response based on question type
        if any(word in message_lower for word in ["how", "steps", "procedure"]):
            # For how-to questions, provide step-by-step answer
            steps = self._extract_procedure_steps(best_match['text'])
            if steps:
                base_response = f"Here's how to {message.lower().replace('how to', '').replace('how do i', '').strip()}:\n\n{steps}"
            else:
                base_response = relevant_text
        
        elif any(word in message_lower for word in ["what", "which", "definition", "meaning"]):
            # For what/which questions, provide direct definition or explanation
            base_response = relevant_text
        
        elif any(word in message_lower for word in ["troubleshoot", "problem", "issue", "error", "fault", "not working"]):
            # For troubleshooting questions, provide specific diagnostic steps
            troubleshooting = self._extract_troubleshooting_steps(best_match['text'])
            if troubleshooting:
                base_response = f"To troubleshoot this issue:\n\n{troubleshooting}"
            else:
                base_response = relevant_text
        
        elif any(word in message_lower for word in ["safety", "safe", "danger", "hazard", "risk"]):
            # For safety questions, provide safety information
            safety_info = self._extract_safety_information(best_match['text'])
            if safety_info:
                base_response = f"Safety information:\n\n{safety_info}"
            else:
                base_response = relevant_text
        
        elif any(word in message_lower for word in ["maintenance", "service", "repair", "maintain"]):
            # For maintenance questions, provide maintenance procedures
            maintenance = self._extract_maintenance_procedures(best_match['text'])
            if maintenance:
                base_response = f"Maintenance procedure:\n\n{maintenance}"
            else:
                base_response = relevant_text
        
        else:
            # For general questions, provide the most relevant information
            base_response = relevant_text
        
        return f"{base_response}\n\n*Source: {best_match['filename']}*"

    async def _generate_gemini_enhanced_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate enhanced response using Gemini AI with full context from multiple documents"""
        try:
            if not self.gemini_available or not self.gemini_client:
                return None
            
            # Compile comprehensive context from all relevant documents
            combined_context = ""
            source_files = []
            
            for i, doc in enumerate(context_info[:3]):  # Use top 3 documents
                source_files.append(doc['filename'])
                combined_context += f"\n--- Document {i+1}: {doc['filename']} (Relevance: {doc['score']:.0%}) ---\n"
                combined_context += doc['text'][:1000]  # Limit per document for context window
                combined_context += "\n"
            
            # Create comprehensive prompt for Gemini 2.5 Flash-Lite
            enhanced_prompt = f"""You are Poornasree AI, an expert technical documentation assistant powered by Google Gemini 2.5 Flash-Lite. You have access to multiple technical documents and should provide comprehensive, accurate, and actionable responses.

CONTEXT DOCUMENTS:
{combined_context}

USER QUESTION: {message}

INSTRUCTIONS:
- Provide a comprehensive, detailed response based on the documentation provided
- Use clear technical language appropriate for the user's expertise level
- Structure your response with clear headings and bullet points for readability
- Include specific steps, procedures, or specifications when relevant
- Highlight any safety considerations or warnings
- If multiple documents contain relevant information, synthesize them into a cohesive answer
- Include specific references to document sections when quoting exact procedures
- Provide practical tips and best practices where applicable
- Format your response professionally with appropriate emojis for visual clarity

Please provide a detailed and helpful response:"""
            
            # Generate response with Gemini
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(
                    enhanced_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1200,  # Increased for comprehensive responses
                        temperature=0.3,  # Lower for more focused technical responses
                        top_p=0.9,
                    )
                )
            )
            
            if response and response.text:
                # Add source attribution
                sources_text = "**Sources:** " + ", ".join(source_files)
                return f"{response.text.strip()}\n\n---\n📚 {sources_text}"
            else:
                logger.warning("Gemini returned empty enhanced response")
                return None
                
        except Exception as e:
            logger.warning(f"Gemini enhanced response failed: {e}")
            return None

    async def _generate_gemini_fallback_response(self, message: str) -> str:
        """Generate fallback response using Gemini 2.5 Flash-Lite when no documents match"""
        try:
            if not self.gemini_available or not self.gemini_client:
                return None
            
            fallback_prompt = f"""You are Poornasree AI, a technical documentation assistant powered by Google Gemini 2.5 Flash-Lite. The user has asked a question but no relevant documents are available in the knowledge base.

USER QUESTION: {message}

INSTRUCTIONS:
- Acknowledge that you don't have specific documentation for this topic
- Provide general technical guidance if the question is about common technical concepts
- Suggest what type of documentation would be helpful to upload
- Offer to help once relevant documentation is provided
- Be helpful and encouraging while being honest about limitations
- Keep the response concise but informative

Please provide a helpful response:"""
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.gemini_client.generate_content(
                    fallback_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=400,
                        temperature=0.5,
                        top_p=0.9,
                    )
                )
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Gemini fallback response failed: {e}")
            return None
    
    async def _generate_ai_enhanced_response(self, message: str, best_match: Dict) -> str:
        """Generate AI-enhanced response using Google Gemini"""
        try:
            # Prepare context for AI
            context = best_match['text'][:1200]  # Increased context for better responses
            filename = best_match['filename']
            
            # Create a focused prompt for technical documentation
            prompt = f"""You are Poornasree AI, a technical documentation assistant. Based on the following documentation excerpt, provide a direct and helpful answer to the user's question.

Documentation from {filename}:
"{context}"

User Question: {message}

Instructions:
- Give a direct, focused answer based primarily on the documentation provided
- Be concise but comprehensive
- Use clear, professional language appropriate for technical documentation
- If the documentation doesn't contain enough information, indicate what additional information might be needed
- Format your response in a clear, easy-to-read structure
- Focus on practical, actionable information

Provide a helpful response:"""
            
            # Try Gemini for enhanced response
            if self.gemini_available and self.gemini_client:
                try:
                    ai_response = await self._query_gemini(prompt, max_tokens=600)
                    
                    if ai_response and len(ai_response.strip()) > 20:
                        logger.info("✅ Gemini enhanced response generated")
                        return ai_response.strip()
                except Exception as e:
                    logger.warning(f"Gemini enhancement failed: {e}")
            
            # If Gemini fails, return None to use fallback response
            return None
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return None
        """Generate comprehensive step-by-step instructional response"""
        best_match = context_info[0] if context_info else None
        if not best_match:
            return """I'd be happy to help you with that! However, I don't have specific information about this topic in the currently uploaded manuals. 

To provide you with accurate, detailed instructions, I need access to the relevant documentation. Here's what you can do:

📋 **Next Steps:**
1. Upload the specific manual or documentation that covers this topic
2. Use the 'Train AI Model' feature to process the documents
3. Ask your question again for detailed, step-by-step guidance

💡 **Tip:** The more specific your question, the better I can help. For example, instead of "how to operate," try "how to start the CNC machine" or "how to set up the cutting parameters."

Would you like to upload the relevant documentation first?"""
        
        # Create comprehensive response
        response = f"""Great question! Let me walk you through this step by step using the information from your '{best_match['filename']}' manual.

## 📖 Overview

Based on your question about "{message}", I've found relevant information that will help you understand the complete process."""
        
        # Extract relevant text
        text = best_match['text']
        
        # Look for numbered steps or bullet points
        if any(pattern in text.lower() for pattern in ['step', '1.', '2.', 'first', 'then', 'next']):
            response += "\n\n## 🔧 Step-by-Step Procedure\n\n"
            procedure_steps = self._extract_procedure_steps(text)
            response += procedure_steps
            
            # Add context and explanation
            response += "\n\n## 💡 Additional Context\n\n"
            additional_info = self._extract_relevant_information(text, message)
            response += additional_info
        else:
            response += "\n\n## 📋 Detailed Information\n\n"
            detailed_info = self._extract_relevant_information(text, message)
            response += detailed_info
        
        # Add safety considerations if available
        if any(word in text.lower() for word in ['safety', 'warning', 'caution', 'danger']):
            safety_info = self._extract_safety_information(text)
            if safety_info:
                response += "\n\n## ⚠️ Safety Considerations\n\n"
                response += safety_info
        
        # Add tips and best practices
        response += "\n\n## 💪 Best Practices\n\n"
        response += """• Always refer to the complete manual for full context
• Take your time with each step - precision is key
• If something doesn't seem right, stop and double-check
• Keep safety protocols in mind throughout the process"""
        
        # Add source information with confidence
        confidence_text = "High" if best_match['score'] > 0.7 else "Medium" if best_match['score'] > 0.4 else "Low"
        response += f"\n\n---\n📚 **Source:** {best_match['filename']} | **Relevance:** {best_match['score']:.0%} ({confidence_text})"
        
        # Offer additional help
        if len(context_info) > 1:
            response += f"\n\n🔍 **Additional Resources:** I found related information in {len(context_info)-1} other section(s) of your documentation. Would you like me to provide those details as well?"
        
        response += "\n\n❓ **Need more help?** Feel free to ask follow-up questions or request clarification on any step!"
        
        return response
    
    def _generate_troubleshooting_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate comprehensive troubleshooting response"""
        response = """# 🔧 Comprehensive Troubleshooting Guide

I understand you're experiencing an issue. Let me help you systematically diagnose and resolve this problem using the information from your technical documentation.

"""
        
        # Add specific troubleshooting from documents
        for i, doc in enumerate(context_info[:2]):
            text = doc['text'].lower()
            
            # Look for troubleshooting keywords
            if any(word in text for word in ['problem', 'issue', 'error', 'fault', 'check', 'verify']):
                response += f"## 📋 Troubleshooting from '{doc['filename']}'\n\n"
                troubleshooting_steps = self._extract_troubleshooting_steps(doc['text'])
                response += troubleshooting_steps
                response += "\n\n"
        
        # Add systematic approach
        response += """## 🎯 Systematic Diagnostic Approach

When troubleshooting any technical issue, I recommend following this proven methodology:

### 🔍 Phase 1: Initial Assessment
1. **Document the symptoms** - Write down exactly what's happening
2. **Note when it started** - Was there a trigger event or change?
3. **Check the obvious first** - Power, connections, switches, indicators
4. **Review recent changes** - Any maintenance, adjustments, or modifications?

### ⚡ Phase 2: Basic Checks
1. **Power supply verification**
   - Check main power connections
   - Verify voltage levels are within specification
   - Look for loose or corroded connections

2. **Safety system status**
   - Ensure all emergency stops are reset
   - Check that safety interlocks are engaged properly
   - Verify protective devices haven't tripped

3. **Visual inspection**
   - Look for obvious damage, wear, or contamination
   - Check for loose components or fasteners
   - Examine cables and connections for damage

### 🔧 Phase 3: Advanced Diagnostics
1. **Error code analysis** - If your system displays error codes, consult the manual
2. **Signal tracing** - Use appropriate test equipment to trace signals
3. **Component testing** - Test individual components as needed
4. **System function testing** - Test related systems that might be affected

## 📞 When to Seek Additional Help

Contact technical support or a qualified technician if:
- The problem involves safety-critical systems
- You encounter electrical hazards
- The issue requires specialized tools or expertise
- Multiple systems are affected simultaneously
- You're unsure about any diagnostic procedure

## 📝 Documentation Tips

Keep a troubleshooting log that includes:
- Date and time of the issue
- Exact symptoms observed
- Steps taken to diagnose/resolve
- Results of each action
- Final resolution method

This helps with future issues and provides valuable maintenance history.

---
💡 **Pro Tip:** Most technical problems have logical causes. Work systematically, don't skip steps, and always prioritize safety over speed."""
        
        return response
    
    def _generate_safety_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate comprehensive safety-focused response"""
        response = """# ⚠️ SAFETY INFORMATION & PROTOCOLS

Safety is paramount in any technical operation. I've gathered relevant safety information from your documentation to ensure you can work safely and effectively.

"""
        
        # Add specific safety info from documents
        has_specific_safety = False
        for doc in context_info[:2]:
            text = doc['text'].lower()
            if any(word in text for word in ['safety', 'warning', 'caution', 'danger', 'hazard']):
                response += f"## 📖 Safety Guidelines from '{doc['filename']}'\n\n"
                safety_info = self._extract_safety_information(doc['text'])
                response += safety_info
                response += "\n\n"
                has_specific_safety = True
        
        if not has_specific_safety:
            response += "## 📖 Document-Specific Safety Information\n\nWhile I found relevant technical information in your documentation, specific safety protocols weren't clearly identified in the matched sections. However, let me provide comprehensive safety guidelines below.\n\n"
        
        # Add comprehensive safety protocols
        response += """## 🛡️ Universal Safety Protocols

### 🔒 Lockout/Tagout (LOTO) Procedures
Before any maintenance or troubleshooting:
1. **Identify all energy sources** (electrical, pneumatic, hydraulic, mechanical)
2. **Shut down equipment** using normal stopping procedures
3. **Isolate energy sources** using appropriate disconnect devices
4. **Lock and tag** all isolation points with personal locks
5. **Verify isolation** by attempting to start equipment (should not operate)
6. **Test for stored energy** and dissipate safely if present

### 👷 Personal Protective Equipment (PPE)
Always wear appropriate PPE based on the task:
- **Eye protection** - Safety glasses with side shields or goggles
- **Hand protection** - Cut-resistant gloves appropriate for the task
- **Foot protection** - Steel-toed safety boots with slip-resistant soles
- **Head protection** - Hard hat in areas with overhead hazards
- **Hearing protection** - Earplugs or earmuffs in high-noise environments

### ⚡ Electrical Safety
- **Never work on live circuits** unless absolutely necessary and properly trained
- **Use proper test equipment** and verify it's functioning before use
- **Maintain safe approach distances** from high-voltage equipment
- **Ensure proper grounding** of all electrical equipment
- **Use arc-rated PPE** when required for electrical work

### 🏃 Emergency Preparedness
- **Know emergency stop locations** and how to activate them quickly
- **Understand evacuation routes** and assembly points
- **Keep first aid kits accessible** and know their locations
- **Report all incidents** immediately, no matter how minor
- **Know who to contact** for different types of emergencies

### 🔧 Safe Work Practices
- **Plan your work** before starting any task
- **Use the right tools** for each job and inspect them before use
- **Maintain good housekeeping** - clean work areas prevent accidents
- **Never bypass safety devices** or disable safety systems
- **Work with a buddy** for complex or potentially hazardous tasks
- **Take breaks** when tired or stressed - fatigue leads to accidents

### 🧠 Mental Safety Checklist
Before starting any task, ask yourself:
- Do I understand the procedure completely?
- Do I have the right tools and PPE?
- Have I identified all potential hazards?
- Is the work area properly prepared and secured?
- Do I know what to do if something goes wrong?

## 🚨 When to Stop Work

Stop immediately and reassess if:
- You encounter unexpected conditions
- Safety equipment fails or is unavailable
- You feel unsure about any procedure
- Environmental conditions change (weather, lighting, etc.)
- You notice signs of fatigue or stress

## 📞 Emergency Contacts

Ensure you have immediate access to:
- Emergency services (911 or local equivalent)
- Plant/facility emergency number
- Supervisor or safety coordinator
- Equipment manufacturer technical support

---
🎯 **Remember:** No task is so urgent that it cannot be done safely. When in doubt, stop and seek guidance."""
        
        return response
    
    def _generate_maintenance_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate comprehensive maintenance-focused response"""
        response = """# 🔧 Comprehensive Maintenance Guide

Proper maintenance is crucial for equipment reliability, safety, and longevity. Let me provide you with detailed maintenance information based on your documentation and industry best practices.

"""
        
        # Add specific maintenance info from documents
        has_specific_maintenance = False
        for doc in context_info[:2]:
            text = doc['text'].lower()
            if any(word in text for word in ['maintenance', 'service', 'lubrication', 'inspection']):
                response += f"## 📋 Maintenance Procedures from '{doc['filename']}'\n\n"
                maintenance_info = self._extract_maintenance_procedures(doc['text'])
                response += maintenance_info
                response += "\n\n"
                has_specific_maintenance = True
        
        if not has_specific_maintenance:
            response += "## 📋 Equipment-Specific Maintenance\n\nWhile I found relevant information in your documentation, specific maintenance procedures weren't clearly identified in the matched sections. Let me provide comprehensive maintenance guidance below.\n\n"
        
        # Add comprehensive maintenance guidance
        response += """## 📅 Maintenance Planning Framework

### 🎯 Types of Maintenance
1. **Preventive Maintenance** - Scheduled maintenance to prevent failures
2. **Predictive Maintenance** - Condition-based maintenance using monitoring
3. **Corrective Maintenance** - Repairs after equipment failure
4. **Condition-Based Maintenance** - Maintenance triggered by equipment condition

### 📊 Maintenance Schedule Development

#### Daily Checks (5-10 minutes)
- Visual inspection for obvious damage or wear
- Check fluid levels (oil, coolant, hydraulic fluid)
- Verify proper operation of safety systems
- Listen for unusual noises or vibrations
- Check for leaks (oil, air, coolant)

#### Weekly Maintenance (30-60 minutes)
- Lubricate grease points per schedule
- Check and clean air filters
- Inspect belts for wear and proper tension
- Verify proper operation of all controls
- Check and record operating parameters
- Clean equipment exterior and work area

#### Monthly Maintenance (2-4 hours)
- Change or service filters (oil, air, hydraulic)
- Inspect electrical connections and components
- Check calibration of measuring instruments
- Perform thorough cleaning of internal components
- Test emergency stop and safety systems
- Review and update maintenance records

#### Quarterly Maintenance (4-8 hours)
- Change fluids per manufacturer recommendations
- Inspect and replace worn components
- Perform alignment checks and adjustments
- Conduct thorough electrical system inspection
- Update spare parts inventory
- Review maintenance procedures and training needs

#### Annual Maintenance (Full Day+)
- Complete equipment overhaul as needed
- Replace major wear items per schedule
- Conduct comprehensive calibration checks
- Update documentation and procedures
- Plan for next year's maintenance budget
- Evaluate equipment performance and reliability

## 🛠️ Essential Maintenance Practices

### 📝 Documentation Requirements
- **Maintenance logs** - Record all work performed
- **Parts tracking** - Monitor parts usage and costs
- **Failure analysis** - Document causes and solutions
- **Performance metrics** - Track reliability and efficiency
- **Vendor information** - Maintain supplier contacts and warranties

### 🔍 Inspection Techniques
- **Visual inspection** - Look for wear, damage, contamination
- **Vibration analysis** - Monitor for bearing or alignment issues
- **Thermal imaging** - Detect hot spots in electrical systems
- **Oil analysis** - Monitor fluid condition and contamination
- **Ultrasonic testing** - Detect leaks and bearing problems

### 🧰 Tool Requirements
Ensure you have proper tools for maintenance:
- Basic hand tools (wrenches, screwdrivers, pliers)
- Torque wrenches for proper fastener tension
- Multimeter for electrical testing
- Grease gun and lubrication equipment
- Cleaning supplies and solvents
- Personal protective equipment (PPE)

### 📦 Spare Parts Management
- **Critical spares** - Keep emergency repair parts in stock
- **Consumables** - Maintain adequate filters, fluids, gaskets
- **Vendor relationships** - Establish reliable parts suppliers
- **Storage conditions** - Proper storage to prevent deterioration
- **Inventory rotation** - Use FIFO (First In, First Out) system

## 💡 Maintenance Best Practices

### 🎯 Proactive Approach
- **Follow manufacturer recommendations** - Adhere to specified intervals
- **Monitor trends** - Track performance over time
- **Address small issues** - Fix problems before they become major
- **Train personnel** - Ensure proper skills and knowledge
- **Use quality parts** - Don't compromise on parts quality

### 📈 Continuous Improvement
- **Analyze failures** - Understand root causes
- **Update procedures** - Incorporate lessons learned
- **Benchmark performance** - Compare with industry standards
- **Invest in training** - Keep skills current
- **Embrace technology** - Use modern maintenance tools

### 💰 Cost Optimization
- **Plan purchases** - Buy parts strategically
- **Standardize components** - Reduce inventory complexity
- **Negotiate contracts** - Establish service agreements
- **Track costs** - Monitor maintenance expenses
- **Measure ROI** - Evaluate maintenance effectiveness

## 🚨 Warning Signs Requiring Immediate Attention

Stop operation and investigate if you notice:
- Unusual noises or vibrations
- Fluid leaks or pressure loss
- Excessive heat or burning smells
- Erratic operation or poor performance
- Safety system malfunctions
- Electrical problems or arcing

---
🎯 **Key Principle:** Maintenance is an investment in reliability, safety, and long-term cost reduction. Well-maintained equipment operates more efficiently, lasts longer, and creates fewer safety hazards."""
        
        return response
    
    def _generate_general_response(self, message: str, context_info: List[Dict]) -> str:
        """Generate comprehensive general response with context"""
        best_match = context_info[0] if context_info else None
        if not best_match:
            return """I'd be happy to help you with that! However, I don't have specific information about this topic in the currently uploaded manuals.

## 🤔 What I Can Help With

As your technical documentation assistant, I can provide detailed guidance on:

### 📚 Equipment Operation
- Step-by-step operating procedures
- Setup and configuration instructions
- Parameter settings and adjustments
- Performance optimization tips

### 🔧 Troubleshooting & Diagnostics
- Systematic problem-solving approaches
- Error code interpretation
- Component testing procedures
- Root cause analysis methods

### 🛡️ Safety Protocols
- Lockout/tagout procedures
- Personal protective equipment requirements
- Emergency response procedures
- Risk assessment techniques

### 🔨 Maintenance & Service
- Preventive maintenance schedules
- Lubrication requirements
- Parts replacement procedures
- Performance monitoring methods

## 💡 To Get the Best Help

1. **Upload relevant documentation** - Technical manuals, service guides, operation instructions
2. **Be specific with questions** - Instead of "How does this work?", try "How do I calibrate the pressure sensor?"
3. **Provide context** - Let me know what equipment or system you're working with
4. **Ask follow-up questions** - I'm here to provide as much detail as you need

## 🚀 Ready to Start?

Upload your technical documentation and ask me anything! I'll provide detailed, step-by-step guidance based on your specific equipment and procedures."""
        
        # Create comprehensive response based on available context
        response = f"""# 📖 Technical Information: {message}

Great question! I've found relevant information in your documentation that will help provide a comprehensive answer.

## 🎯 Based on Your Documentation

From your '{best_match['filename']}' manual, here's what I found:

"""
        
        # Extract and present relevant information
        detailed_info = self._extract_relevant_information(best_match['text'], message)
        response += detailed_info
        
        # Add analysis and context
        response += "\n\n## 💡 Analysis & Context\n\n"
        
        # Provide additional context based on the type of information
        if any(word in message.lower() for word in ['operation', 'operate', 'run', 'start', 'use']):
            response += """This appears to be related to equipment operation. When working with any technical equipment:

🔍 **Before You Begin:**
- Ensure you understand all safety requirements
- Verify that all prerequisites are met
- Have the complete manual available for reference

⚡ **During Operation:**
- Follow the sequence exactly as documented
- Monitor for any unusual behavior or responses
- Keep safety systems active and accessible

✅ **After Completion:**
- Verify that the operation completed successfully
- Document any observations or issues
- Return equipment to a safe, stable state"""
        
        elif any(word in message.lower() for word in ['setup', 'install', 'configure', 'calibrate']):
            response += """This relates to equipment setup or configuration. For successful setup:

📋 **Preparation Phase:**
- Gather all required tools and materials
- Review the complete procedure before starting
- Ensure proper environmental conditions

🔧 **Implementation Phase:**
- Follow the documented sequence precisely
- Verify each step before proceeding to the next
- Document settings and parameters as you go

🎯 **Verification Phase:**
- Test all functions after setup
- Compare results with expected performance
- Keep records of final configuration settings"""
        
        elif any(word in message.lower() for word in ['specification', 'parameter', 'setting', 'value']):
            response += """This appears to involve technical specifications or parameters. When working with specs:

📊 **Understanding Parameters:**
- Always use manufacturer-specified values
- Understand the tolerance ranges allowed
- Know the consequences of out-of-spec conditions

⚖️ **Measurement & Verification:**
- Use calibrated instruments for critical measurements
- Take multiple readings to ensure accuracy
- Document all readings and conditions

🔄 **Adjustment Procedures:**
- Make small, incremental changes
- Allow time for stabilization between adjustments
- Verify that changes produce expected results"""
        
        else:
            response += """Based on the context of your question, here are some general guidelines:

🎓 **Learning Approach:**
- Start with understanding the fundamentals
- Build knowledge progressively from basic to advanced
- Practice procedures in safe, controlled conditions

🔍 **Verification Methods:**
- Cross-reference information across multiple sources
- Validate understanding through practical application
- Seek clarification when uncertainty exists

📈 **Continuous Improvement:**
- Keep detailed records of procedures and results
- Learn from both successes and challenges
- Stay updated with latest best practices and updates"""
        
        # Add source information and additional resources
        confidence_text = "High" if best_match['score'] > 0.7 else "Medium" if best_match['score'] > 0.4 else "Low"
        response += f"""

## 📚 Source Information

**Document:** {best_match['filename']}
**Relevance Score:** {best_match['score']:.0%} ({confidence_text} confidence)
**Match Quality:** {"Excellent" if best_match['score'] > 0.8 else "Good" if best_match['score'] > 0.6 else "Fair"}"""
        
        # Offer additional help
        if len(context_info) > 1:
            response += f"""

## 🔍 Additional Resources Available

I found related information in {len(context_info)-1} other section(s) of your documentation. These additional sources might provide:
- Alternative procedures or methods
- Additional safety considerations
- Troubleshooting information
- Related specifications or parameters

Would you like me to provide information from these additional sources as well?"""
        
        response += """

## ❓ Need More Information?

If you need clarification or have follow-up questions:
- Ask for more specific details about any aspect
- Request examples or practical applications
- Inquire about related procedures or considerations
- Ask about potential issues or troubleshooting

I'm here to provide as much detail as you need to successfully complete your task!"""
        
        return response
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate concise fallback response when no documents match"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey", "greeting"]):
            return "Hello! I'm Poornasree AI, your technical documentation assistant. I can help you with machine manuals, troubleshooting, maintenance procedures, and safety information. Upload your manuals and ask me specific questions!"

        elif any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            return """I can help you with:
• Equipment operation procedures
• Troubleshooting and diagnostics  
• Safety protocols and guidelines
• Maintenance schedules and procedures
• Technical specifications and settings

Upload your technical manuals first, then ask specific questions about your equipment."""

        # Default response for unmatched queries
        return f"I don't have specific information about '{message}' in the currently uploaded manuals. Please upload relevant technical documentation and ask your question again for accurate, detailed answers."
    
    def _extract_procedure_steps(self, text: str) -> str:
        """Extract and format step-by-step procedures from text"""
        lines = text.split('\n')
        procedure_lines = []
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            # Look for existing numbered steps
            if any(pattern in line.lower() for pattern in ['step', '1.', '2.', '3.', '4.', '5.']):
                if len(line) > 10:
                    # Clean up the formatting
                    clean_line = re.sub(r'^(step\s*\d+[:\.]?\s*)', '', line, flags=re.IGNORECASE)
                    clean_line = re.sub(r'^\d+[\.\)]\s*', '', clean_line)
                    procedure_lines.append(f"{step_counter}. {clean_line}")
                    step_counter += 1
            # Look for action words
            elif any(word in line.lower() for word in ['ensure', 'check', 'verify', 'set', 'adjust', 'turn', 'press']):
                if len(line) > 15 and step_counter <= 8:
                    procedure_lines.append(f"{step_counter}. {line}")
                    step_counter += 1
        
        if not procedure_lines:
            # Fallback: create steps from sentences
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            for i, sentence in enumerate(sentences[:5]):
                if any(word in sentence.lower() for word in ['turn', 'press', 'check', 'set', 'adjust']):
                    procedure_lines.append(f"{i+1}. {sentence}.")
        
        return '\n'.join(procedure_lines[:8])  # Limit to 8 steps
    
    def _extract_relevant_information(self, text: str, query: str) -> str:
        """Extract most relevant information from text based on query"""
        query_words = [word.lower() for word in query.split() if len(word) > 2]
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
        
        scored_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = 0
            
            # Score based on query word matches
            for word in query_words:
                if word in sentence_lower:
                    score += 2
            
            # Boost score for actionable content
            if any(action in sentence_lower for action in ['check', 'verify', 'ensure', 'adjust', 'set']):
                score += 1
            
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # Sort by relevance and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored_sentences[:3]]
        
        return '. '.join(top_sentences) + '.' if top_sentences else text[:200] + "..."
    
    def _extract_troubleshooting_steps(self, text: str) -> str:
        """Extract troubleshooting steps from text"""
        lines = text.split('\n')
        troubleshooting_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['check', 'verify', 'ensure', 'test', 'inspect']):
                if len(line) > 15:
                    troubleshooting_lines.append(f"• {line}")
        
        return '\n'.join(troubleshooting_lines[:6])  # Limit to 6 steps
    
    def _extract_safety_information(self, text: str) -> str:
        """Extract safety information from text"""
        lines = text.split('\n')
        safety_lines = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['warning', 'caution', 'danger', 'safety', 'never', 'always', 'must']):
                if len(line) > 15:
                    safety_lines.append(f"⚠️ {line}")
        
        return '\n'.join(safety_lines[:5])  # Limit to 5 safety points
    
    def _extract_maintenance_procedures(self, text: str) -> str:
        """Extract and format maintenance procedures from text"""
        lines = text.split('\n')
        maintenance_lines = []
        
        for line in lines:
            line = line.strip()
            # Look for maintenance action words
            if any(word in line.lower() for word in ['lubricate', 'clean', 'replace', 'inspect', 'service', 'maintain']):
                if len(line) > 15:
                    # Categorize maintenance actions
                    if any(word in line.lower() for word in ['lubricate', 'oil', 'grease']):
                        maintenance_lines.append(f"🛢️ **Lubrication:** {line}")
                    elif any(word in line.lower() for word in ['clean', 'wash', 'remove dirt', 'debris']):
                        maintenance_lines.append(f"🧹 **Cleaning:** {line}")
                    elif any(word in line.lower() for word in ['replace', 'change', 'substitute']):
                        maintenance_lines.append(f"🔄 **Replacement:** {line}")
                    elif any(word in line.lower() for word in ['inspect', 'check', 'examine', 'verify']):
                        maintenance_lines.append(f"🔍 **Inspection:** {line}")
                    else:
                        maintenance_lines.append(f"🔧 **Maintenance:** {line}")
            # Look for schedule-related information
            elif any(word in line.lower() for word in ['daily', 'weekly', 'monthly', 'annually', 'hours', 'schedule']):
                if len(line) > 15:
                    maintenance_lines.append(f"📅 **Schedule:** {line}")
        
        # Look for part numbers or specifications
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in ['part number', 'specification', 'torque', 'pressure', 'temperature']):
                if len(line) > 15 and not any(existing in line for existing in [s.split(':', 1)[1] if ':' in s else s for s in maintenance_lines]):
                    maintenance_lines.append(f"� **Specification:** {line}")
        
        return '\n\n'.join(maintenance_lines[:10])  # Limit to 10 maintenance items
    
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

    def _calculate_enhanced_confidence(self, message: str, relevant_docs: List[Dict]) -> float:
        """Enhanced confidence calculation considering Gemini AI usage"""
        base_confidence = self._calculate_confidence(message, relevant_docs)
        
        # Boost confidence when using Gemini 2.5 Flash-Lite
        if self.gemini_available:
            # Gemini 2.5 Flash-Lite provides more accurate and contextual responses
            gemini_boost = 0.15 if relevant_docs else 0.1
            enhanced_confidence = min(base_confidence + gemini_boost, 0.98)  # Cap at 98% for Gemini 2.5 Flash-Lite
        else:
            enhanced_confidence = base_confidence
        
        return round(enhanced_confidence, 3)
    
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
        
        # Determine active AI model
        ai_model_info = {
            "gemini_available": self.gemini_available,
            "gemini_model": self.gemini_model if self.gemini_available else None,
            "active_ai": None
        }
        
        if self.gemini_available:
            ai_model_info["active_ai"] = f"Google Gemini ({self.gemini_model})"
        else:
            ai_model_info["active_ai"] = "Local processing only"
        
        capabilities = [
            "Advanced Document Search",
            "Context-Aware Responses", 
            "Technical Troubleshooting",
            "Maintenance Guidance",
            "Safety Information",
            "Procedure Extraction",
            "Multi-Document Analysis"
        ]
        
        # Add AI-specific capabilities
        if self.gemini_available:
            capabilities.extend([
                "Google Gemini AI Enhancement",
                "Advanced Language Understanding",
                "Intelligent Response Generation",
                "Natural Conversation Flow"
            ])
        
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
            "ai_models": ai_model_info,
            "capabilities": capabilities
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
