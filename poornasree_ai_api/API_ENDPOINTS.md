# 🔗 Poornasree AI API - Complete Endpoints Reference

## 📋 API Overview

**Base URL**: `http://localhost:8000`  
**API Version**: v2.0.0  
**Documentation**: http://localhost:8000/docs  
**Alternative Docs**: http://localhost:8000/redoc  

---

## 🏠 Core Endpoints

### 🌟 **Root Endpoint**
```http
GET /
```
**Description**: Welcome message with API information and quick endpoint overview  
**Response**: API status, version, features list, and main endpoints

---

## 💊 Health & Monitoring

### ✅ **Health Check**
```http
GET /health
```
**Description**: Comprehensive health check with system metrics  
**Returns**: 
- API status and uptime
- Database connectivity status
- AI service health
- System metrics (CPU, memory, disk)
- Indian Standard Time timestamp

---

## 🤖 AI Management

### 📊 **AI Service Status**
```http
GET /api/v1/ai/status
```
**Description**: Detailed AI service status including Gemini integration  
**Returns**: AI initialization status, model info, performance metrics

### 🧠 **AI Model Information**
```http
GET /api/v1/ai/model-info
```
**Description**: Detailed information about the AI model configuration  
**Returns**: Model specifications, capabilities, and configuration details

### 🧪 **Test AI Service**
```http
POST /api/v1/ai/test
```
**Description**: Test AI service functionality with sample queries  
**Body**: `{"test_type": "basic", "query": "optional test query"}`  
**Returns**: Test results and AI response validation

### 🔄 **Reinitialize AI Service**
```http
POST /api/v1/ai/reinitialize
```
**Description**: Force reinitialize the AI service (troubleshooting)  
**Returns**: Reinitialization status and new service state

---

## 💬 Chat & Conversation

### 🗨️ **Chat with AI**
```http
POST /api/v1/chat
```
**Description**: Main chat endpoint for AI conversations about machine manuals  
**Body**:
```json
{
  "message": "Your question here",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```
**Returns**: AI response with confidence score, processing time, and metadata

### 📜 **Get Chat History**
```http
GET /api/v1/chat/history
```
**Query Parameters**: 
- `user_id` (optional): Filter by user
- `session_id` (optional): Filter by session
- `limit` (optional): Number of messages to return (default: 50)

**Returns**: Paginated chat history with timestamps

### 🧹 **Clear Chat History**
```http
DELETE /api/v1/chat/history
```
**Query Parameters**:
- `user_id` (optional): Clear for specific user
- `session_id` (optional): Clear specific session

**Returns**: Deletion confirmation and affected records count

---

## 📄 Document Management

### 📤 **Upload Document**
```http
POST /api/v1/documents/upload
```
**Description**: Upload and process machine manuals (PDF, DOCX, TXT, XLSX)  
**Body**: `multipart/form-data`
- `file`: Document file
- `description` (optional): Document description
- `user_id` (optional): User identifier

**Returns**: Processing results, extracted content summary, and document ID

### 📋 **List Documents**
```http
GET /api/v1/documents/list
```
**Query Parameters**:
- `user_id` (optional): Filter by user
- `limit` (optional): Number of documents (default: 20)
- `offset` (optional): Pagination offset

**Returns**: List of uploaded documents with metadata

### 📖 **Get Document Details**
```http
GET /api/v1/documents/{document_id}
```
**Description**: Get detailed information about a specific document  
**Returns**: Document metadata, processing status, and content summary

### 🗑️ **Delete Document**
```http
DELETE /api/v1/documents/{document_id}
```
**Description**: Remove document from system and knowledge base  
**Returns**: Deletion confirmation

### 🔍 **Search Documents**
```http
POST /api/v1/documents/search
```
**Body**:
```json
{
  "query": "search terms",
  "limit": 10,
  "user_id": "optional_user_id"
}
```
**Returns**: Relevant document excerpts with similarity scores

---

## 🎓 Service Guide Training

### 📚 **Train Service Guide**
```http
POST /api/v1/service-guide/train-service-guide
```
**Description**: Train AI with Excel or PDF service guide data  
**Body**: `multipart/form-data`
- `file`: Excel (.xlsx, .xls) or PDF file
- `user_id` (optional): User identifier

**Returns**: Training results and knowledge base updates

### 📊 **Get Training Status**
```http
GET /api/v1/service-guide/training-status
```
**Description**: Check status of ongoing or recent training operations  
**Returns**: Training progress, completion status, and results summary

### 📈 **List Training Sessions**
```http
GET /api/v1/service-guide/training-sessions
```
**Query Parameters**:
- `limit` (optional): Number of sessions (default: 10)
- `user_id` (optional): Filter by user

**Returns**: Historical training sessions with results

### 🧪 **Test Training Data**
```http
POST /api/v1/service-guide/test-training
```
**Body**:
```json
{
  "query": "test question",
  "training_session_id": "optional_session_id"
}
```
**Returns**: Test results against trained knowledge base

---

## 📊 Statistics & Analytics

### 📈 **Get Usage Statistics**
```http
GET /api/v1/documents/stats
```
**Description**: Get system usage statistics  
**Returns**: Document counts, chat statistics, user activity metrics

### 🔍 **Get Search Analytics**
```http
GET /api/v1/chat/analytics
```
**Query Parameters**:
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `user_id` (optional): Filter by user

**Returns**: Search patterns, popular queries, and usage trends

---

## 🔧 System Administration

### 🗄️ **Database Status**
```http
GET /api/v1/system/database-status
```
**Description**: Detailed database connection and table status  
**Returns**: Connection info, table counts, and health metrics

### 🧹 **System Cleanup**
```http
POST /api/v1/system/cleanup
```
**Description**: Clean up temporary files and optimize system  
**Returns**: Cleanup results and space freed

### 📊 **System Metrics**
```http
GET /api/v1/system/metrics
```
**Description**: Detailed system performance metrics  
**Returns**: CPU, memory, disk usage, and API performance stats

---

## 🚨 Error Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Authentication required |
| `404` | Not Found - Resource doesn't exist |
| `413` | Payload Too Large - File size exceeded |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error - System error |
| `503` | Service Unavailable - AI service down |

---

## 📝 Request/Response Examples

### 💬 **Chat Example**

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I maintain a CNC machine?",
    "user_id": "user123"
  }'
```

**Response**:
```json
{
  "response": "To maintain a CNC machine properly...",
  "confidence_score": 0.92,
  "processing_time": 1.45,
  "timestamp": "2025-07-29T10:30:00+05:30",
  "session_id": "sess_abc123",
  "metadata": {
    "model_used": "gemini-2.5-flash-lite",
    "sources_used": ["cnc_manual.pdf", "maintenance_guide.docx"]
  }
}
```

### 📤 **Document Upload Example**

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@manual.pdf" \
  -F "description=CNC Machine Manual" \
  -F "user_id=user123"
```

**Response**:
```json
{
  "success": true,
  "document_id": "doc_xyz789",
  "filename": "manual.pdf",
  "file_size": 2048576,
  "processing_time": 3.21,
  "content_summary": "CNC machine operating procedures...",
  "pages_processed": 45,
  "chunks_created": 123
}
```

---

## 🛠️ SDK & Integration

### 🐍 **Python Example**
```python
import requests

# Chat with AI
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"message": "How to calibrate sensors?"}
)
print(response.json()["response"])

# Upload document
with open("manual.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f},
        data={"description": "Equipment Manual"}
    )
print(response.json())
```

### 🌐 **JavaScript/Flutter Example**
```javascript
// Chat request
const chatResponse = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: 'What are the safety procedures?',
    user_id: 'user123'
  })
});
const chatData = await chatResponse.json();
console.log(chatData.response);
```

---

## 🔄 Rate Limits

- **Chat Endpoint**: 60 requests/minute per user
- **Document Upload**: 10 files/minute per user  
- **Health Check**: No limit
- **AI Status**: 30 requests/minute per user

---

## 🎯 Quick Testing

**Test API availability**:
```bash
curl http://localhost:8000/health
```

**Test AI chat**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc  
- **Startup Guide**: `STARTUP_GUIDE.md`
- **Project Overview**: `PROJECT_OVERVIEW.md`

---

**🎉 Ready to build amazing AI-powered applications with Poornasree AI API!**
