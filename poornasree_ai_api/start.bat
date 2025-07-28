@echo off
echo Starting Poornasree AI Chatbot API...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create data directories
echo Creating data directories...
if not exist "data\" mkdir data
if not exist "data\uploads\" mkdir data\uploads
if not exist "data\chroma_db\" mkdir data\chroma_db
if not exist "data\logs\" mkdir data\logs

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo.
echo ========================================
echo  Poornasree AI Chatbot API
echo ========================================
echo  Starting server on http://localhost:8000
echo  API Documentation: http://localhost:8000/docs
echo  Health Check: http://localhost:8000/health
echo ========================================
echo.

REM Start the API
python main.py

pause
