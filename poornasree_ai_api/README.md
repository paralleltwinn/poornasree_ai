# Poornasree AI Chatbot API

A **free** FastAPI-based chatbot API for machine manuals and technical documentation. Uses local AI models and requires no API keys for basic functionality.

## 🚀 Features

- **Free AI Models**: Uses Hugging Face transformers (no API keys required)
- **Document Processing**: Upload PDFs, Word docs, and text files
- **Vector Search**: Find relevant information from uploaded manuals
- **Flutter Integration**: CORS-enabled for web app integration
- **Local Storage**: No external database dependencies
- **Fast Deployment**: Ready for Railway, Render, or Docker

## 📋 Quick Start

### 1. Local Development

```bash
# Navigate to API directory
cd poornasree_ai_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads data/chroma_db data/logs

# Start the API
python main.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Docker Deployment

```bash
# Build Docker image
docker build -t poornasree-ai-api .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data poornasree-ai-api
```

### 3. Free Cloud Deployment

#### Railway (Recommended)
1. Push code to GitHub
2. Connect to Railway.app
3. Deploy automatically
4. Get free HTTPS URL

#### Render
1. Connect GitHub repository
2. Select "Web Service"
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🔧 API Endpoints

### Chat Endpoints
- `POST /api/v1/chat` - Send message to chatbot
- `GET /api/v1/chat/status` - Check chat service status
- `GET /api/v1/chat/examples` - Get example questions

### Document Endpoints
- `POST /api/v1/documents/upload` - Upload manual/document
- `GET /api/v1/documents/supported-formats` - Get supported file types
- `GET /api/v1/documents/stats` - Get upload statistics
- `POST /api/v1/documents/search` - Search uploaded documents

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /health/ai` - AI service status

## 💬 Using the Chat API

### Send a Message
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "How do I start the machine?",
  "user_id": "user123"
}'
```

### Response Format
```json
{
  "response": "To start the machine, follow these steps...",
  "confidence": 0.85,
  "sources": ["manual_chapter_2.pdf"],
  "timestamp": "2025-07-28T10:30:00",
  "processing_time": 1.2
}
```

## 📄 Document Upload

### Upload a Manual
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
-F "file=@machine_manual.pdf" \
-F "description=Main machine manual"
```

### Supported Formats
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)
- Maximum file size: 10MB

## 🔗 Flutter Integration

Update your Flutter app's chat service:

```dart
class ChatService {
  static const String baseUrl = 'YOUR_API_URL'; // e.g., Railway URL
  
  Future<String> sendMessage(String message) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'message': message,
        'user_id': 'flutter_user'
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['response'];
    }
    throw Exception('Failed to get response');
  }
}
```

## 🆓 Free Tier Specifications

### What's Free:
- ✅ Unlimited local AI processing
- ✅ Document upload and processing
- ✅ Vector search and retrieval
- ✅ All API endpoints
- ✅ Railway/Render hosting (with limits)

### Limitations:
- 🔄 Response time: 2-5 seconds (local models)
- 📁 File size: 10MB per document
- 💾 Storage: Limited by hosting provider
- 🧠 AI quality: Good but not as advanced as GPT-4

### Upgrade Options:
To improve AI quality, add these to `.env`:
```bash
# For better responses (paid)
OPENAI_API_KEY=your_key_here
# Then uncomment OpenAI usage in ai_service.py
```

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:
- `API_PORT=8000` - Server port
- `MAX_FILE_SIZE_MB=10` - Upload limit
- `LOG_LEVEL=INFO` - Logging level

## 📊 Monitoring

### Check API Status
```bash
curl http://localhost:8000/health/detailed
```

### View Logs
```bash
tail -f data/logs/api.log
```

## 🚀 Deployment URLs

After deploying to a free service, update your Flutter app:

```dart
// Update this in your Flutter app
static const String baseUrl = 'https://your-app.railway.app';
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Models not loading**:
   ```bash
   # Clear cache and restart
   rm -rf ~/.cache/huggingface
   python main.py
   ```

2. **Port already in use**:
   ```bash
   # Change port in main.py or kill process
   lsof -ti:8000 | xargs kill -9
   ```

3. **Memory issues**:
   ```bash
   # Use smaller models in ai_service.py
   # Replace DialoGPT-small with DialoGPT-micro
   ```

## 📈 Performance Tips

1. **Faster responses**: Use smaller models
2. **Better quality**: Upload more specific manuals
3. **Reduce memory**: Limit concurrent requests
4. **Scale up**: Add caching and load balancing

## 🔄 Updates

To upgrade the API:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py
```

## 📞 Support

- Check `/health/detailed` for system status
- Review logs in `data/logs/api.log`
- Test with `/docs` interactive interface

---

**Built with ❤️ using FastAPI, Hugging Face, and ChromaDB**

*Free, fast, and ready for production!*
