#!/usr/bin/env python3
"""
Complete test for Gemini 2.5 Flash-Lite integration with the AI service
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.ai_service import AIService

async def test_complete_integration():
    """Complete test of Gemini integration"""
    print("🚀 Complete Gemini 2.5 Flash-Lite Integration Test")
    print("=" * 60)
    
    # Environment check
    print("1. Environment Configuration:")
    api_key = os.getenv('GEMINI_API_KEY')
    model = os.getenv('GEMINI_MODEL')
    print(f"   🔑 API Key: {'✅ SET' if api_key else '❌ NOT SET'}")
    print(f"   🤖 Model: {model}")
    
    if not api_key:
        print("❌ No API key found. Please check .env file.")
        return
    
    # Initialize AI service
    print("\n2. AI Service Initialization:")
    ai_service = AIService()
    
    try:
        await ai_service.initialize()
        print("   ✅ AI service initialized")
        
        # Check status
        status = ai_service.get_status()
        print(f"   📊 Service Status:")
        print(f"      Model: {status.get('model_name', 'Unknown')}")
        print(f"      Gemini Available: {status.get('ai_models', {}).get('gemini_available', False)}")
        print(f"      Active AI: {status.get('ai_models', {}).get('active_ai', 'Unknown')}")
        print(f"      Status: {status.get('status', 'Unknown')}")
        print(f"      Documents: {status.get('document_count', 0)}")
        
        # Test basic chat
        print("\n3. Testing Chat Functionality:")
        test_queries = [
            "Hello! How are you?",
            "What can you help me with?",
            "Explain safety protocols in a manufacturing environment."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {query}")
            try:
                response = await ai_service.chat(
                    message=query,
                    session_id="test_session"
                )
                
                print(f"   ✅ Response received!")
                print(f"   📝 Content: {response['response'][:100]}...")
                print(f"   🎯 Confidence: {response['confidence']}")
                print(f"   🔧 AI Used: {response.get('ai_used', 'Unknown')}")
                print(f"   ⏱️ Time: {response.get('processing_time', 'Unknown')}s")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎉 Integration test completed!")
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_integration())
