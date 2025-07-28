# Poornasree AI - Machine Manual Chatbot

A Flutter web application that provides an AI-powered chatbot interface for machine manuals with document upload and training capabilities.

## 🚀 Quick Start

### Prerequisites
- Flutter SDK (3.0.0 or higher)
- Python 3.8+ (for the API backend)
- Web browser (Chrome/Edge recommended)

### 1. Start the Backend API

```bash
cd poornasree_ai_api
pip install -r requirements.txt
python main.py
```

The API will start on `http://localhost:8000`

### 2. Run the Flutter Web App

```bash
flutter pub get
flutter run -d chrome
```

## 📋 Features

### ✅ Completed Features
- **Modern Flutter Web Interface** - Clean Material 3 design
- **AI-Powered Chat** - Conversation with confidence scores
- **Document Upload Dashboard** - Drag & drop file uploads
- **Free AI Models** - Using Hugging Face transformers (local)
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
- **AI Models**: Hugging Face (DialoGPT-small, sentence-transformers)
- **Vector DB**: ChromaDB (local storage)
- **Document Processing**: PyPDF2, python-docx
- **CORS**: Enabled for web development

## 💰 Cost Analysis

### Development Costs: **$0** (All Free)
- Hugging Face models (free local execution)
- ChromaDB (free local storage)
- FastAPI (open source)
- Flutter (open source)

### Hosting Costs: **$0** (Free Tiers)
- API: Railway/Render free tier
- Web App: GitHub Pages/Netlify free tier
- No external API costs (local AI models)

**Status**: ✅ Production Ready
