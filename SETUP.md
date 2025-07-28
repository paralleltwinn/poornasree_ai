# Setup Guide for Poornasree AI

## Step 1: Install Python

### Option A: Download from Python.org (Recommended)
1. Go to https://python.org/downloads/
2. Download Python 3.8 or newer
3. Run the installer with "Add Python to PATH" checked
4. Verify: `python --version`

### Option B: Using Microsoft Store
1. Open Microsoft Store
2. Search for "Python 3.11" or newer
3. Install and verify: `python --version`

## Step 2: Setup Backend API

```powershell
# Navigate to API directory
cd "d:\MY PROJECTS\poornasreeAI\poornasree_ai\poornasree_ai_api"

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
```

The API will be available at: http://localhost:8000

## Step 3: Run Flutter Web App

```powershell
# Navigate to Flutter project
cd "d:\MY PROJECTS\poornasreeAI\poornasree_ai"

# Install Flutter dependencies (already done)
flutter pub get

# Start the web application
flutter run -d chrome
```

## 🧪 Testing the Complete Stack

1. **Test API Health**: Open http://localhost:8000/health in browser
2. **Test API Docs**: Open http://localhost:8000/docs for interactive API
3. **Test Flutter App**: Should open automatically in Chrome

## 🚀 Quick Start Commands

After Python is installed:

```powershell
# Terminal 1 - Start API
cd "d:\MY PROJECTS\poornasreeAI\poornasree_ai\poornasree_ai_api"
pip install fastapi uvicorn transformers torch chromadb pypdf2 python-docx sentence-transformers python-multipart
python main.py

# Terminal 2 - Start Flutter
cd "d:\MY PROJECTS\poornasreeAI\poornasree_ai"
flutter run -d chrome
```

## 🎯 Expected Results

- **API**: Console shows "Uvicorn running on http://127.0.0.1:8000"
- **Flutter**: Browser opens with the app interface
- **Features**: Upload documents in Dashboard, chat in Chat screen

## 🔧 Troubleshooting

### Python Installation Issues
- Restart terminal/VS Code after Python installation
- Check PATH environment variable includes Python
- Use `python -m pip` if `pip` command not found

### Flutter Issues
- Run `flutter doctor` to check setup
- Ensure Chrome browser is available
- Check for Windows firewall blocking connections

### API Connection Issues
- Verify API is running on port 8000
- Check Windows firewall allows local connections
- Ensure no other service is using port 8000

---

**Next Steps**: Once Python is installed, run the commands above to start both services!
