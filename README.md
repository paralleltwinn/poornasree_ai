# Poornasree AI - Machine Manual Chatbot

A Flutter web application that provides an AI-powered chatbot interface for machine manuals with document upload and training capabilities.

## 🚀 Quick Start

### Prerequisites
- Flutter SDK (3.0.0 or higher)
- Python 3.8+ (for the API backend)
- Web browser (Chrome/Edge recommended)

### 1. Start the Backend API (One Command!)

```bash
cd poornasree_ai_api
python startup.py
```

**That's it!** The startup script will:
- ✅ Auto-install all required libraries
- ✅ Test database & AI connections
- ✅ Start the API server at `http://localhost:8000`

### 2. Run the Flutter Web App

```bash
flutter pub get
flutter run -d chrome
```

## 📁 Essential Files

### 🎯 **Core Files You Need to Know**

```
📦 Project Root
├── 🚀 poornasree_ai_api/
│   ├── ⭐ startup.py           # One-command startup (start here!)
│   ├── 🚀 main.py             # FastAPI application entry point
│   ├── 📋 requirements.txt    # All Python dependencies
│   ├── ⚙️ .env               # Environment configuration
│   ├── 🧹 complete_cleanup.py # Complete database & file cleanup
│   ├── ⚡ quick_cleanup.py    # Quick database-only cleanup
│   ├── 🔗 API_ENDPOINTS.md   # Complete API endpoints reference
│   ├── 🧹 CLEANUP_GUIDE.md   # Database cleanup instructions
│   └── 📖 STARTUP_GUIDE.md   # Detailed setup instructions
│
├── 📱 lib/
│   ├── 🏠 main.dart          # Flutter app entry point
│   ├── 📱 screens/           # App screens (Home, Chat, Dashboard)
│   ├── 🤖 services/          # API communication services
│   └── 🎨 widgets/           # Reusable UI components
│
├── 📋 pubspec.yaml           # Flutter dependencies
└── 📖 README.md              # This file
```

### 🔧 **For Developers Only**

```
📦 Advanced Files (Optional)
├── 🧪 poornasree_ai_api/tests/     # Test suite
├── 🔧 poornasree_ai_api/utils/     # Utility scripts
├── 🎓 poornasree_ai_api/training/  # AI training scripts
└── 📄 poornasree_ai_api/sample_data/ # Test documents
```

## 📋 Features

### ✅ Completed Features
- **Modern Flutter Web Interface** - Clean Material 3 design
- **AI-Powered Chat** - Conversation with confidence scores
- **Document Upload Dashboard** - Drag & drop file uploads
- **Automated Setup** - One-command startup with auto-install
- **Vector Search** - ChromaDB for document embeddings
- **Production Architecture** - Modular code structure
- **Health Monitoring** - API status indicators

### 🎯 Main Screens
1. **Home** - Navigation hub with welcome interface
2. **Chat** - AI conversation with example questions
3. **Dashboard** - Upload training documents and statistics

## 🛠️ Technology Stack

### Frontend (Flutter Web)
- **Framework**: Flutter 3.x with Material 3
- **State Management**: Provider
- **HTTP Client**: http package
- **File Upload**: file_picker
- **Storage**: shared_preferences

### Backend (Python API)
- **Framework**: FastAPI
- **AI Models**: Google Gemini 2.5 Flash-Lite
- **Vector DB**: ChromaDB + FAISS (local storage)
- **Document Processing**: PyPDF2, python-docx, openpyxl
- **Database**: MySQL with SQLAlchemy
- **CORS**: Enabled for web development

## 💰 Cost Analysis

### Development Costs: **$0** (All Free)
- Google Gemini free tier (API key required)
- ChromaDB (free local storage)
- FastAPI (open source)
- Flutter (open source)

### Hosting Costs: **$0** (Free Tiers)
- API: Railway/Render free tier
- Web App: GitHub Pages/Netlify free tier
- Minimal API costs (Gemini free tier)

**Status**: ✅ Production Ready

## 🚀 Get Started

**New to the project?** Just run:
```bash
cd poornasree_ai_api
python startup.py
```

**Need to clean database?** Choose your cleanup level:
```bash
# Quick cleanup (database only)
python quick_cleanup.py

# Complete cleanup (database + files)
python complete_cleanup.py
```

**Need help?** Check these guides:
- `poornasree_ai_api/STARTUP_GUIDE.md` - Setup instructions
- `poornasree_ai_api/CLEANUP_GUIDE.md` - Database cleanup guide
- `poornasree_ai_api/API_ENDPOINTS.md` - Complete API reference

---

🎉 **Your AI-powered document chatbot will be running at:**
- 🌐 **Web App**: http://localhost:3000 (Flutter)
- 🔗 **API**: http://localhost:8000 (FastAPI)
- 📚 **API Docs**: http://localhost:8000/docs
- 🔗 **All Endpoints**: See `poornasree_ai_api/API_ENDPOINTS.md`
