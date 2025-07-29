#!/usr/bin/env python3
"""
Quick test script for Poornasree AI Chatbot API
Run this to verify the API is working correctly
"""

import requests
import json
import time
import sys

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        return False

def test_chat_endpoint():
    """Test chat functionality"""
    print("💬 Testing chat endpoint...")
    try:
        payload = {
            "message": "Hello, how can you help me?",
            "user_id": "test_user"
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data['response'][:100]}...")
            return True
        else:
            print(f"❌ Chat test failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def test_document_formats():
    """Test supported document formats"""
    print("📄 Testing document formats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/documents/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supported formats: {data['supported_formats']}")
            return True
        else:
            print(f"❌ Document formats test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document formats test error: {e}")
        return False

def test_examples_endpoint():
    """Test examples endpoint"""
    print("💡 Testing examples endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/examples")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['examples'])} example categories")
            return True
        else:
            print(f"❌ Examples test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Examples test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Poornasree AI API Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_chat_endpoint,
        test_document_formats,
        test_examples_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
        time.sleep(1)  # Brief pause between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
        print()
        print("Next steps:")
        print("1. Upload a manual: POST /api/v1/documents/upload")
        print("2. Ask questions: POST /api/v1/chat")
        print("3. Check docs: http://localhost:8000/docs")
    else:
        print("⚠️ Some tests failed. Check the API logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
