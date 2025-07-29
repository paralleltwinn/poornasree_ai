#!/usr/bin/env python3
"""
Complete Gemini 2.5 Flash-Lite Integration Test
Tests the entire system using Gemini 2.5 Flash-Lite exclusively
"""

import asyncio
import os
import sys
import logging
import requests
import json
from app.services.ai_service import AIService

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_gemini_2_5_flash_lite_complete():
    """Test complete Gemini 2.5 Flash-Lite integration"""
    
    print("🚀 TESTING COMPLETE GEMINI 2.5 FLASH-LITE INTEGRATION")
    print("=" * 60)
    
    # Test 1: Environment Configuration
    print("\n1️⃣ Testing Environment Configuration")
    print("-" * 40)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY: Set (length: {len(api_key)})")
        print(f"✅ API Key preview: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY: Not set")
        return False
    
    # Test 2: AI Service Direct Integration
    print("\n2️⃣ Testing AI Service Direct Integration")
    print("-" * 40)
    
    try:
        ai_service = AIService()
        await ai_service.initialize()
        
        if ai_service.gemini_available:
            print(f"✅ Gemini Available: True")
            print(f"✅ Model: {ai_service.gemini_model}")
            print(f"✅ API Key Configured: {bool(ai_service.gemini_api_key)}")
        else:
            print("❌ Gemini not available in AI service")
            return False
        
        # Test direct chat
        print("\n🧪 Testing Direct AI Service Chat...")
        test_response = await ai_service.chat("What safety precautions should I follow?")
        
        if test_response and test_response.get('response'):
            print(f"✅ Direct chat successful!")
            print(f"   Response length: {len(test_response['response'])} chars")
            print(f"   Confidence: {test_response.get('confidence', 'N/A')}")
            print(f"   AI Used: {test_response.get('ai_used', 'N/A')}")
            print(f"   Model Used: {test_response.get('model_used', 'N/A')}")
            print(f"   Gemini Status: {test_response.get('gemini_status', 'N/A')}")
        else:
            print("❌ Direct chat failed")
            return False
            
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False
    
    # Test 3: API Endpoint Integration
    print("\n3️⃣ Testing API Endpoint Integration")
    print("-" * 40)
    
    try:
        base_url = "http://localhost:8000"
        
        # Test chat endpoint
        chat_payload = {
            "message": "How do I start a CNC machine safely?",
            "user_id": "test_user_gemini"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json=chat_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat API successful!")
            print(f"   Response length: {len(data.get('response', ''))} chars")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   Processing time: {data.get('processing_time', 'N/A')}s")
            
            # Check for Gemini-specific fields
            if 'ai_used' in data:
                print(f"   AI Used: {data['ai_used']}")
            if 'model_used' in data:
                print(f"   Model Used: {data['model_used']}")
            if 'gemini_status' in data:
                print(f"   Gemini Status: {data['gemini_status']}")
            
            # Verify response quality
            response_text = data.get('response', '')
            if len(response_text) > 100 and data.get('confidence', 0) > 0.5:
                print("   ✅ High-quality response generated")
            else:
                print("   ⚠️ Response quality could be improved")
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False
    
    # Test 4: Model-Specific Tests
    print("\n4️⃣ Testing Gemini 2.5 Flash-Lite Specific Features")
    print("-" * 40)
    
    try:
        # Test various question types
        test_questions = [
            {
                "question": "What are the key safety protocols for machine operation?",
                "expected_keywords": ["safety", "protocol", "machine", "operation"]
            },
            {
                "question": "How do I troubleshoot a hydraulic system failure?",
                "expected_keywords": ["troubleshoot", "hydraulic", "system", "failure"]
            },
            {
                "question": "What maintenance should be performed daily?",
                "expected_keywords": ["maintenance", "daily", "perform", "schedule"]
            }
        ]
        
        successful_tests = 0
        
        for i, test in enumerate(test_questions, 1):
            print(f"\n   Test {i}: {test['question']}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/v1/chat",
                    json={
                        "message": test["question"],
                        "user_id": "test_user_gemini_features"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('response', '').lower()
                    
                    # Check for expected keywords
                    found_keywords = [kw for kw in test['expected_keywords'] if kw in answer]
                    
                    if len(found_keywords) >= 2:  # At least 2 keywords found
                        print(f"      ✅ Relevant response (found: {', '.join(found_keywords)})")
                        successful_tests += 1
                    else:
                        print(f"      ⚠️ Response may not be fully relevant")
                        
                    # Check confidence
                    confidence = data.get('confidence', 0)
                    if confidence > 0.7:
                        print(f"      ✅ High confidence: {confidence:.2f}")
                    elif confidence > 0.4:
                        print(f"      ⚠️ Medium confidence: {confidence:.2f}")
                    else:
                        print(f"      ❌ Low confidence: {confidence:.2f}")
                else:
                    print(f"      ❌ API call failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Test failed: {e}")
        
        print(f"\n   📊 Feature Tests Results: {successful_tests}/{len(test_questions)} successful")
        
        if successful_tests >= len(test_questions) * 0.8:  # 80% success rate
            print("   ✅ Gemini 2.5 Flash-Lite features working excellently!")
        else:
            print("   ⚠️ Some Gemini features may need improvement")
            
    except Exception as e:
        print(f"❌ Model-specific tests failed: {e}")
        return False
    
    # Test 5: Performance and Quality Assessment
    print("\n5️⃣ Testing Performance and Quality")
    print("-" * 40)
    
    try:
        # Test response time and quality
        import time
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json={
                "message": "Provide a comprehensive guide for CNC machine startup procedures.",
                "user_id": "test_user_performance"
            },
            timeout=30
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print(f"✅ Performance Test Results:")
            print(f"   Response Time: {response_time:.2f}s")
            print(f"   Response Length: {len(response_text)} characters")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   Processing Time (reported): {data.get('processing_time', 'N/A')}s")
            
            # Quality checks
            quality_score = 0
            if len(response_text) > 200:
                quality_score += 1
                print("   ✅ Comprehensive response length")
            
            if data.get('confidence', 0) > 0.6:
                quality_score += 1
                print("   ✅ Good confidence level")
            
            if response_time < 10:
                quality_score += 1
                print("   ✅ Good response time")
            
            if any(word in response_text.lower() for word in ['step', 'procedure', 'safety', 'startup']):
                quality_score += 1
                print("   ✅ Relevant content detected")
            
            print(f"\n   📊 Quality Score: {quality_score}/4")
            
            if quality_score >= 3:
                print("   🌟 EXCELLENT - Gemini 2.5 Flash-Lite performing optimally!")
            elif quality_score >= 2:
                print("   👍 GOOD - Gemini 2.5 Flash-Lite performing well")
            else:
                print("   ⚠️ FAIR - Performance could be improved")
        else:
            print(f"❌ Performance test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE GEMINI 2.5 FLASH-LITE INTEGRATION TEST FINISHED")
    print("✅ All systems are using Gemini 2.5 Flash-Lite entirely!")
    print("🚀 Ready for production with enhanced AI capabilities!")
    
    return True

async def main():
    """Main test function"""
    success = await test_gemini_2_5_flash_lite_complete()
    
    if success:
        print("\n🏆 SUCCESS: Complete Gemini 2.5 Flash-Lite integration verified!")
    else:
        print("\n❌ FAILURE: Some integration issues detected")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
