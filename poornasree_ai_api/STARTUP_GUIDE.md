# 🚀 Poornasree AI - Quick Startup Guide

## ⚡ One-Command Startup

The Poornasree AI API now features a comprehensive startup system that automatically:

- ✅ **Checks & Installs** all required libraries
- ✅ **Verifies Environment** configuration (.env file)
- ✅ **Tests Database** connection and setup
- ✅ **Validates Gemini AI** integration
- ✅ **Tests Core Features** (AI service, document processing)
- ✅ **Starts the Server** automatically if all tests pass

## 🎯 How to Use

### Option 1: Python Script (Recommended)
```bash
python startup.py
```

### Option 2: Windows Batch File
```bash
quick_start.bat
```

### Option 3: PowerShell (Windows)
```powershell
.\quick_start.ps1
```

## 📋 What the Startup Script Does

### 🔍 **Step 1: Library Verification**
- Checks all 30+ required libraries from `requirements.txt`
- Automatically installs missing packages
- Reports installation status for each library

### ⚙️ **Step 2: Environment Configuration**
- Loads `.env` file variables
- Verifies critical settings:
  - Database connection details
  - Gemini API key
  - Application configuration

### 🗃️ **Step 3: Database Testing**
- Tests MySQL connection
- Verifies database schema
- Initializes tables if needed
- Reports connection status

### 🤖 **Step 4: Gemini AI Verification**
- Tests Google Gemini API connection
- Validates API key functionality
- Confirms AI model availability

### 🧠 **Step 5: AI Service Testing**
- Initializes AI service
- Tests chat functionality
- Verifies knowledge base loading
- Reports service status

### 📄 **Step 6: Document Processing**
- Tests PDF, Word, Excel processing
- Verifies sample file handling
- Reports supported formats

### 🌐 **Step 7: API Endpoint Validation**
- Verifies FastAPI app creation
- Checks route registration
- Confirms server readiness

### 🚀 **Step 8: Automatic Server Start**
- Starts FastAPI server on success
- Opens on `http://localhost:8000`
- Provides API docs at `/docs`

## 📊 Example Output

```
🚀 POORNASREE AI - STARTUP SEQUENCE
============================================================
🔍 CHECKING LIBRARY DEPENDENCIES
============================================================
✅ fastapi is available
✅ uvicorn is available
⚠️  transformers is missing
ℹ️  Installing transformers==4.36.0...
✅ Successfully installed transformers
✅ All required libraries are available!

⚙️ LOADING ENVIRONMENT CONFIGURATION  
============================================================
✅ DB_HOST: RDP-Main-Server
✅ DB_PORT: 3306
✅ GEMINI_API_KEY: **************************
✅ Environment configuration loaded successfully!

🗃️ TESTING DATABASE CONNECTION
============================================================
ℹ️  Testing database connection...
✅ Database connection successful!
✅ Database initialization completed!

🤖 TESTING GEMINI AI INTEGRATION
============================================================
ℹ️  Testing Gemini API connection...
✅ Gemini responded: Connection successful!
✅ Gemini AI integration working!

📊 TEST SUMMARY
============================================================
✅ Libraries: PASSED
✅ Environment: PASSED  
✅ Database: PASSED
✅ Gemini: PASSED
✅ Ai Service: PASSED
✅ Document Processing: PASSED
✅ Api Endpoints: PASSED

ℹ️  Tests passed: 7/7
🎉 All critical tests passed! Starting server...

🚀 STARTING POORNASREE AI API SERVER
============================================================
ℹ️  Server will be available at: http://localhost:8000
ℹ️  API documentation: http://localhost:8000/docs
```

## 🛠️ Troubleshooting

### ❌ Libraries Failed
```bash
# Manual installation
pip install -r requirements.txt

# Or update pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### ❌ Environment Failed
- Check `.env` file exists in the root directory
- Verify all required variables are set:
  ```
  DB_HOST=RDP-Main-Server
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=your_password
  DB_NAME=psrAI
  GEMINI_API_KEY=your_api_key
  ```

### ❌ Database Failed
```bash
# Create database manually
python utils/create_database.py
python utils/create_database_tables.py
```

### ❌ Gemini Failed
- Verify your Gemini API key is correct
- Check internet connection
- Ensure API key has proper permissions

## 🎯 Development Workflow

### For Daily Development:
```bash
python startup.py  # Full system check + start server
```

### For Quick Start (if already tested):
```bash
python main.py  # Direct server start
```

### For Testing Only:
```bash
python startup.py  # Will run tests but you can Ctrl+C before server starts
```

## 🔧 Advanced Usage

### Custom Testing:
The startup script can be imported and used programmatically:

```python
from startup import run_comprehensive_tests

async def custom_test():
    results = await run_comprehensive_tests()
    return results
```

### Environment-Specific Startup:
Set environment variables to control behavior:
```bash
export SKIP_TESTS=true  # Skip comprehensive tests
export AUTO_INSTALL=false  # Don't auto-install packages
```

## 📈 Benefits

1. **Zero-Setup Development**: New developers can start immediately
2. **Automatic Problem Detection**: Catches issues before they cause problems
3. **Consistent Environment**: Ensures all developers have the same setup
4. **Faster Debugging**: Clear error messages and suggested fixes
5. **Production Readiness**: Validates all systems before deployment

---

**🎉 Enjoy hassle-free development with Poornasree AI!**
