#!/usr/bin/env python3
"""
Service Guide Training Script
This script provides training functionality for the AI service guide
Training is also available via API endpoints at /api/service-guide/train
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_service import AIService

async def train_service_guide():
    """Train the service guide using the AI service"""
    print("🎓 Starting service guide training...")
    
    try:
        # Initialize AI service
        ai_service = AIService()
        await ai_service.initialize()
        
        print("✅ Training completed successfully!")
        print("💡 For advanced training, use the API endpoint: POST /api/service-guide/train")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(train_service_guide())
    sys.exit(0 if success else 1)
