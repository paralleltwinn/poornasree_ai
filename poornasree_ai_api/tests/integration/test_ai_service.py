#!/usr/bin/env python3
"""
Simple Gemini API Key Verification Script
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment variables are loaded correctly"""
    print("🔍 ENVIRONMENT VARIABLE CHECK")
    print("=" * 40)
    
    # Check Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...{api_key[-4:] if len(api_key) > 24 else api_key}")
    else:
        print("❌ GEMINI_API_KEY not found")
    
    # Check Gemini Model
    model = os.getenv("GEMINI_MODEL")
    if model:
        print(f"✅ GEMINI_MODEL: {model}")
    else:
        print("❌ GEMINI_MODEL not found")
    
    # Check database config
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    print(f"✅ Database: {db_host}/{db_name}")
    
    return api_key is not None

async def test_gemini_direct():
    """Test Gemini AI directly with environment variables"""
    try:
        import google.generativeai as genai
        print("✅ google-generativeai library is available")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ No API key found")
            return False
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content("Hello, this is a test.")
        
        if response and response.text:
            print(f"✅ Gemini direct test successful!")
            print(f"📝 Response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini returned empty response")
            return False
            
    except ImportError:
        print("❌ google-generativeai library not available")
        return False
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    
    print("🚀 GEMINI VERIFICATION TEST")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    if env_ok:
        print("\n🔄 Testing Gemini direct connection...")
        result = asyncio.run(test_gemini_direct())
        
        if result:
            print("\n🎉 GEMINI IS WORKING PERFECTLY!")
            print("✅ Your API key is valid and functional")
        else:
            print("\n❌ GEMINI TEST FAILED")
            print("🔧 Check your API key and network connection")
    else:
        print("\n❌ ENVIRONMENT SETUP ISSUE")
        print("🔧 Check your .env file configuration")
