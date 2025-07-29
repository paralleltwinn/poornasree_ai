#!/usr/bin/env python3
"""
Complete Gemini Integration Test
Tests the entire system with Gemini AI powering all responses
"""

import asyncio
import requests
import time
import json
from app.services.ai_service import AIService

# API Configuration
API_BASE_URL = "http://localhost:8000"

async def test_gemini_ai_service():
    """Test Gemini AI service directly"""
    print("🤖 TESTING GEMINI AI SERVICE DIRECTLY")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    await ai_service.initialize()
    
    # Check Gemini status
    status = ai_service.get_status()
    print(f"📊 AI Service Status:")
    print(f"   Initialized: {status.get('initialized', False)}")
    print(f"   Model: {status.get('model_name', 'Unknown')}")
    print(f"   Documents: {status.get('documents_count', 0)}")
    print(f"   Gemini Available: {ai_service.gemini_available}")
    print(f"   Gemini Model: {ai_service.gemini_model}")
    
    if not ai_service.gemini_available:
        print("❌ Gemini not available - check API key configuration")
        return False
    
    # Test direct Gemini chat
    print(f"\n🔄 Testing direct Gemini chat...")
    test_messages = [
        "Hello, how are you?",
        "What can you help me with?",
        "Explain safety protocols in manufacturing",
        "How do I troubleshoot a CNC machine?",
        "What maintenance should I perform daily?"
    ]
    
    successful_tests = 0
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: {message}")
        try:
            result = await ai_service.chat(message, session_id="gemini_test")
            
            if result and result.get("response"):
                print(f"   ✅ Response: {result['response'][:100]}...")
                print(f"   🎯 Confidence: {result.get('confidence', 0):.2f}")
                print(f"   🤖 AI Used: {result.get('ai_used', 'Unknown')}")
                print(f"   ⚡ Processing: {result.get('processing_time', 0):.2f}s")
                print(f"   🧠 Gemini Status: {result.get('gemini_status', 'unknown')}")
                
                if "Gemini" in result.get('ai_used', ''):
                    successful_tests += 1
                    print(f"   🌟 GEMINI POWERED!")
                else:
                    print(f"   ⚠️ Using fallback AI")
            else:
                print(f"   ❌ Failed: No response")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Direct AI Test Results: {successful_tests}/{len(test_messages)} using Gemini")
    return successful_tests >= len(test_messages) * 0.8  # 80% success rate

def test_api_endpoints():
    """Test API endpoints for Gemini integration"""
    print("\n🔗 TESTING API ENDPOINTS")
    print("=" * 50)
    
    # Test chat endpoint
    test_questions = [
        {
            "message": "Hello, I need help with machine operation",
            "expected_features": ["gemini", "ai", "help"]
        },
        {
            "message": "What safety precautions should I follow?",
            "expected_features": ["safety", "precaution", "protocol"]
        },
        {
            "message": "How do I perform maintenance?",
            "expected_features": ["maintenance", "procedure", "step"]
        },
        {
            "message": "The machine won't start, what should I check?",
            "expected_features": ["troubleshoot", "check", "start"]
        },
        {
            "message": "What does error code E001 mean?",
            "expected_features": ["error", "code", "meaning"]
        }
    ]
    
    successful_tests = 0
    gemini_responses = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n   Test {i}: {test['message']}")
        try:
            payload = {
                "message": test["message"],
                "user_id": "gemini_test_user",
                "session_id": "gemini_api_test"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                confidence = data.get('confidence', 0)
                ai_used = data.get('ai_used', 'Unknown')
                model_used = data.get('model_used', 'Unknown')
                processing_time = data.get('processing_time', 0)
                
                print(f"   ✅ API Response received")
                print(f"   📝 Length: {len(response_text)} characters")
                print(f"   🎯 Confidence: {confidence:.2f}")
                print(f"   🤖 AI Used: {ai_used}")
                print(f"   🧠 Model: {model_used}")
                print(f"   ⚡ Processing: {processing_time:.2f}s")
                print(f"   🌐 Total Time: {end_time - start_time:.2f}s")
                
                # Check if response is using Gemini
                if "Gemini" in ai_used or "Gemini" in model_used:
                    gemini_responses += 1
                    print(f"   🌟 GEMINI AI POWERED!")
                
                # Check response quality
                response_lower = response_text.lower()
                found_features = [feat for feat in test['expected_features'] 
                                if feat in response_lower]
                
                if len(response_text) > 50 and confidence > 0.3:
                    successful_tests += 1
                    print(f"   ✅ Quality check passed")
                    if found_features:
                        print(f"   🎯 Found features: {', '.join(found_features)}")
                else:
                    print(f"   ⚠️ Quality check failed - response too short or low confidence")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request Error: {e}")
    
    print(f"\n📊 API Test Results:")
    print(f"   Total Tests: {len(test_questions)}")
    print(f"   Successful: {successful_tests}")
    print(f"   Gemini Powered: {gemini_responses}")
    print(f"   Success Rate: {(successful_tests/len(test_questions)*100):.1f}%")
    print(f"   Gemini Rate: {(gemini_responses/len(test_questions)*100):.1f}%")
    
    return successful_tests >= len(test_questions) * 0.8

def test_flutter_integration():
    """Test Flutter-specific API features"""
    print("\n📱 TESTING FLUTTER INTEGRATION")
    print("=" * 50)
    
    # Test status endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ai/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ AI Status endpoint working")
            print(f"   Model: {status.get('model_name', 'Unknown')}")
            print(f"   Initialized: {status.get('initialized', False)}")
            print(f"   Documents: {status.get('documents_count', 0)}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False
    
    # Test model info endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ai/model-info", timeout=10)
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ Model info endpoint working")
            print(f"   Available models: {len(model_info.get('available_models', []))}")
        else:
            print(f"❌ Model info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info endpoint error: {e}")
        return False
    
    # Test AI test endpoint
    try:
        payload = {"test_message": "Flutter integration test with Gemini AI"}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/ai/test",
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            test_result = response.json()
            print(f"✅ AI test endpoint working")
            print(f"   Response length: {len(test_result.get('response', ''))}")
            print(f"   AI model: {test_result.get('ai_model', 'Unknown')}")
            if "Gemini" in test_result.get('ai_model', ''):
                print(f"   🌟 GEMINI AI CONFIRMED!")
        else:
            print(f"❌ AI test endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI test endpoint error: {e}")
        return False
    
    print(f"✅ Flutter integration tests passed")
    return True

async def run_comprehensive_gemini_test():
    """Run comprehensive Gemini integration test"""
    print("🚀 COMPREHENSIVE GEMINI INTEGRATION TEST")
    print("📋 Testing complete Gemini AI integration across all components")
    print("🎯 Goal: Verify Gemini powers the entire Flutter chat system")
    print("=" * 70)
    
    test_results = {}
    
    # Test 1: Direct AI Service
    print("\n🔍 PHASE 1: DIRECT AI SERVICE TEST")
    test_results['ai_service'] = await test_gemini_ai_service()
    
    # Test 2: API Endpoints
    print("\n🔍 PHASE 2: API ENDPOINTS TEST")
    test_results['api_endpoints'] = test_api_endpoints()
    
    # Test 3: Flutter Integration
    print("\n🔍 PHASE 3: FLUTTER INTEGRATION TEST")
    test_results['flutter_integration'] = test_flutter_integration()
    
    # Final Results
    print("\n" + "=" * 70)
    print("🏁 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 90:
        print("🌟 EXCELLENT: Gemini integration is working perfectly!")
        print("🚀 Flutter chat is now powered entirely by Gemini AI!")
    elif success_rate >= 75:
        print("👍 GOOD: Gemini integration is mostly working")
        print("⚠️ Some minor issues need attention")
    elif success_rate >= 50:
        print("⚠️ FAIR: Gemini integration has significant issues")
        print("🔧 Major improvements needed")
    else:
        print("❌ POOR: Gemini integration is not working properly")
        print("🛠️ Complete system review required")
    
    print("\n💡 Next Steps:")
    if success_rate >= 90:
        print("   • Test Flutter app with enhanced Gemini responses")
        print("   • Monitor response quality and performance")
        print("   • Deploy to production environment")
    else:
        print("   • Review failed test components")
        print("   • Check Gemini API configuration")
        print("   • Verify network connectivity and permissions")
    
    return success_rate >= 75

if __name__ == "__main__":
    asyncio.run(run_comprehensive_gemini_test())
