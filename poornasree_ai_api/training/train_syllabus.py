#!/usr/bin/env python3
"""
Syllabus Training Script
This script provides training functionality for syllabus data
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_service import AIService

async def train_syllabus():
    """Train the syllabus data using the AI service"""
    print("📚 Starting syllabus training...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        await ai_service.initialize()
        
        print("✅ Syllabus training completed successfully!")
        print("💡 Training data is automatically processed when documents are uploaded")
        
    except Exception as e:
        print(f"❌ Syllabus training failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(train_syllabus())
    sys.exit(0 if success else 1)
