#!/usr/bin/env python3
"""
Enhanced AI Setup Script for Poornasree AI
This script sets up the production-ready AI environment with advanced capabilities
"""

import subprocess
import sys
import os
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a shell command with error handling"""
    logger.info(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    logger.info("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.8+")
        return False

def create_directories():
    """Create necessary directories"""
    logger.info("📁 Creating directories...")
    directories = [
        "./data",
        "./data/uploads", 
        "./data/logs",
        "./data/knowledge_base",
        "./data/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install required Python packages"""
    logger.info("📦 Installing dependencies...")
    
    # Core dependencies first
    core_packages = [
        "pip --upgrade",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "aiomysql==0.2.0",
        "pymysql==1.1.0"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    # AI/ML dependencies
    ai_packages = [
        "torch==2.1.1",
        "transformers==4.36.0", 
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
        "nltk==3.8.1"
    ]
    
    for package in ai_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            logger.warning(f"⚠️ Failed to install {package} - continuing without it")
    
    # Document processing
    doc_packages = [
        "PyPDF2==3.0.1",
        "python-docx==1.1.0", 
        "docx2txt==0.8",
        "aiofiles==23.2.1"
    ]
    
    for package in doc_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def download_ai_models():
    """Download and cache AI models"""
    logger.info("🤖 Setting up AI models...")
    
    # Create a simple script to download models
    setup_script = """
import logging
logging.basicConfig(level=logging.INFO)

try:
    from sentence_transformers import SentenceTransformer
    import torch
    
    print("Setting up sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Sentence transformer model ready")
    
    print("Testing model...")
    test_embedding = model.encode(["This is a test sentence"])
    print(f"Model test successful - embedding shape: {test_embedding.shape}")
    
except ImportError as e:
    print(f"Some AI libraries not available: {e}")
    print("Basic functionality will work without advanced AI features")
    
except Exception as e:
    print(f"Error setting up AI models: {e}")
"""
    
    with open("setup_models.py", "w", encoding="utf-8") as f:
        f.write(setup_script)
    
    run_command("python setup_models.py", "Setting up AI models")
    
    # Cleanup
    if os.path.exists("setup_models.py"):
        os.remove("setup_models.py")

def create_config_file():
    """Create enhanced configuration file"""
    logger.info("⚙️ Creating configuration...")
    
    config_content = """# Poornasree AI Enhanced Configuration

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Database Settings
DATABASE_URL=mysql+aiomysql://root:123%40456@RDP-Main-Server/psrapp

# AI Settings
AI_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_SEARCH_RESULTS=10

# Document Processing
MAX_FILE_SIZE_MB=10
SUPPORTED_FORMATS=pdf,docx,doc,txt
UPLOAD_DIR=./data/uploads

# Performance Settings
MAX_WORKERS=4
EMBEDDING_BATCH_SIZE=32
SEARCH_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/logs/api.log

# Features
ENABLE_EMBEDDINGS=true
ENABLE_ADVANCED_SEARCH=true
ENABLE_DOCUMENT_ANALYSIS=true
ENABLE_CONTEXT_AWARE_RESPONSES=true
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    logger.info("✅ Configuration file created")

def test_installation():
    """Test if the installation is working"""
    logger.info("🧪 Testing installation...")
    
    test_script = """
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    try:
        import fastapi
        logger.info("✅ FastAPI available")
        
        import sqlalchemy
        logger.info("✅ SQLAlchemy available")
        
        import PyPDF2
        logger.info("✅ PDF processing available")
        
        try:
            import sentence_transformers
            logger.info("✅ Advanced AI features available")
        except ImportError:
            logger.warning("⚠️ Advanced AI features not available - basic functionality will work")
        
        try:
            import sklearn
            logger.info("✅ Machine learning features available")
        except ImportError:
            logger.warning("⚠️ ML features not available - basic search will work")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Critical import failed: {e}")
        return False

def test_directories():
    import os
    directories = ['./data', './data/uploads', './data/logs']
    for directory in directories:
        if os.path.exists(directory):
            logger.info(f"✅ Directory exists: {directory}")
        else:
            logger.error(f"❌ Directory missing: {directory}")
            return False
    return True

if __name__ == "__main__":
    logger.info("🔍 Running installation tests...")
    
    if test_imports() and test_directories():
        logger.info("🎉 Installation test successful!")
        logger.info("🚀 Ready to start Poornasree AI Enhanced!")
        sys.exit(0)
    else:
        logger.error("❌ Installation test failed")
        sys.exit(1)
"""
    
    with open("test_installation.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    success = run_command("python test_installation.py", "Running installation tests")
    
    # Cleanup
    if os.path.exists("test_installation.py"):
        os.remove("test_installation.py")
    
    return success

def main():
    """Main setup function"""
    logger.info("🚀 Starting Poornasree AI Enhanced Setup")
    logger.info("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Download AI models
    download_ai_models()
    
    # Create config
    create_config_file()
    
    # Test installation
    if test_installation():
        logger.info("=" * 60)
        logger.info("🎉 SETUP COMPLETE!")
        logger.info("=" * 60)
        logger.info("📋 Next steps:")
        logger.info("1. Start the API server: python main.py")
        logger.info("2. Open browser: http://localhost:8000/docs")
        logger.info("3. Test with Flutter app: http://localhost:3000")
        logger.info("4. Upload documents and train the AI")
        logger.info("")
        logger.info("🚀 Enhanced Features Available:")
        logger.info("• Advanced document processing with smart chunking")
        logger.info("• Semantic search with sentence embeddings")
        logger.info("• Context-aware AI responses")
        logger.info("• Production-ready performance optimizations")
        logger.info("• Persistent knowledge base storage")
        logger.info("")
        logger.info("📖 For help, check the documentation or run with --help")
    else:
        logger.error("❌ Setup completed with errors - check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()
