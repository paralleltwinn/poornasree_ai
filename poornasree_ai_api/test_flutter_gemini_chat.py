#!/usr/bin/env python3
"""
Test Flutter Chat with Gemini Integration
Verify that the Flutter chat API is now powered entirely by Gemini
"""

import requests
import json
import time

def test_flutter_chat_with_gemini():
    """Test Flutter chat endpoints to verify Gemini integration"""
    print("📱 TESTING FLUTTER CHAT WITH GEMINI AI")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test questions that Flutter app would send
    flutter_test_questions = [
        {
            "message": "Hello! I'm using the Flutter app and need help",
            "expected": "response should be Gemini-powered"
        },
        {
            "message": "How do I start my CNC machine safely?",
            "expected": "detailed procedural response"
        },
        {
            "message": "What safety equipment do I need?",
            "expected": "comprehensive safety information"
        },
        {
            "message": "My machine shows error E001, what should I do?",
            "expected": "troubleshooting guidance"
        },
        {
            "message": "When should I perform maintenance?",
            "expected": "maintenance schedule information"
        }
    ]
    
    print(f"🔄 Testing {len(flutter_test_questions)} Flutter chat scenarios...")
    
    successful_tests = 0
    gemini_responses = 0
    
    for i, test in enumerate(flutter_test_questions, 1):
        print(f"\n📨 Test {i}: {test['message']}")
        print("-" * 50)
        
        try:
            # Simulate Flutter app request
            payload = {
                "message": test["message"],
                "user_id": "flutter_test_user",
                "session_id": f"flutter_session_{int(time.time())}"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/v1/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract response details
                response_text = data.get("response", "")
                confidence = data.get("confidence", 0)
                ai_used = data.get("ai_used", "Unknown")
                model_used = data.get("model_used", "Unknown")
                api_processing_time = data.get("processing_time", 0)
                gemini_status = data.get("gemini_status", "unknown")
                source_docs = data.get("source_documents", [])
                
                print(f"✅ Response received successfully")
                print(f"📝 Response length: {len(response_text)} characters")
                print(f"🎯 Confidence score: {confidence:.2f}")
                print(f"🤖 AI model used: {ai_used}")
                print(f"🧠 Model details: {model_used}")
                print(f"⚡ API processing: {api_processing_time:.2f}s")
                print(f"🌐 Total time: {processing_time:.2f}s")
                print(f"🔧 Gemini status: {gemini_status}")
                print(f"📚 Source documents: {len(source_docs)}")
                
                # Check if using Gemini
                is_gemini_powered = (
                    "Gemini" in str(ai_used) or 
                    "Gemini" in str(model_used) or 
                    gemini_status == "active"
                )
                
                if is_gemini_powered:
                    gemini_responses += 1
                    print(f"🌟 GEMINI AI POWERED: ✅")
                else:
                    print(f"⚠️ Using fallback AI (not Gemini)")
                
                # Check response quality
                if len(response_text) > 100 and confidence > 0.5:
                    successful_tests += 1
                    print(f"✅ Quality check: PASSED")
                    
                    # Show preview of response
                    preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                    print(f"📖 Response preview: {preview}")
                else:
                    print(f"❌ Quality check: FAILED (too short or low confidence)")
                
                # Show source attribution if available
                if source_docs:
                    print(f"📋 Sources:")
                    for j, doc in enumerate(source_docs[:2], 1):
                        filename = doc.get("filename", "Unknown")
                        score = doc.get("score", 0)
                        print(f"   {j}. {filename} (relevance: {score:.0%})")
                        
            else:
                print(f"❌ API request failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print(f"⏱️ Request timed out after 30 seconds")
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
    
    # Summary results
    print(f"\n" + "=" * 60)
    print(f"📊 FLUTTER CHAT TEST RESULTS")
    print(f"=" * 60)
    print(f"Total tests: {len(flutter_test_questions)}")
    print(f"Successful responses: {successful_tests}")
    print(f"Gemini-powered responses: {gemini_responses}")
    print(f"Success rate: {(successful_tests/len(flutter_test_questions)*100):.1f}%")
    print(f"Gemini utilization: {(gemini_responses/len(flutter_test_questions)*100):.1f}%")
    
    # Final assessment
    if gemini_responses >= len(flutter_test_questions) * 0.8:
        print(f"\n🌟 EXCELLENT: Flutter chat is powered by Gemini AI!")
        print(f"🚀 Ready for production deployment with enhanced AI responses")
    elif gemini_responses >= len(flutter_test_questions) * 0.5:
        print(f"\n👍 GOOD: Most responses are Gemini-powered")
        print(f"⚠️ Some optimization may be needed")
    else:
        print(f"\n⚠️ NEEDS IMPROVEMENT: Low Gemini utilization")
        print(f"🔧 Check Gemini configuration and availability")
    
    return gemini_responses >= len(flutter_test_questions) * 0.8

def test_flutter_api_metadata():
    """Test Flutter-specific API metadata"""
    print(f"\n🔍 TESTING FLUTTER API METADATA")
    print(f"=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test chat endpoint metadata
        response = requests.post(
            f"{base_url}/api/v1/chat",
            json={
                "message": "Test Flutter metadata",
                "user_id": "flutter_metadata_test"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Flutter API metadata test passed")
            print(f"📊 Metadata fields available:")
            
            expected_fields = [
                "response", "confidence", "ai_used", "model_used", 
                "processing_time", "source_documents", "gemini_status"
            ]
            
            for field in expected_fields:
                if field in data:
                    print(f"   ✅ {field}: {type(data[field]).__name__}")
                else:
                    print(f"   ❌ {field}: Missing")
            
            # Check if all required fields are present
            missing_fields = [field for field in expected_fields if field not in data]
            if not missing_fields:
                print(f"🌟 All Flutter metadata fields present!")
                return True
            else:
                print(f"⚠️ Missing fields: {', '.join(missing_fields)}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Metadata test error: {e}")
        return False

def main():
    """Main test function"""
    print(f"🚀 FLUTTER CHAT + GEMINI INTEGRATION TEST")
    print(f"📋 Verify Flutter app can access Gemini-powered responses")
    print(f"🎯 Goal: 80%+ Gemini utilization for Flutter chat")
    print(f"\n" + "=" * 70)
    
    # Run tests
    chat_success = test_flutter_chat_with_gemini()
    metadata_success = test_flutter_api_metadata()
    
    # Final assessment
    print(f"\n" + "=" * 70)
    print(f"🏁 FINAL ASSESSMENT")
    print(f"=" * 70)
    
    if chat_success and metadata_success:
        print(f"🌟 EXCELLENT: Flutter chat is fully integrated with Gemini AI!")
        print(f"✅ Chat responses: Gemini-powered")
        print(f"✅ API metadata: Complete")
        print(f"🚀 Ready for Flutter app deployment!")
        
        print(f"\n💡 Next steps:")
        print(f"   • Build and test Flutter app")
        print(f"   • Verify UI shows Gemini indicators")
        print(f"   • Test various question types")
        print(f"   • Monitor response quality")
        
    elif chat_success:
        print(f"👍 GOOD: Chat is Gemini-powered but metadata needs work")
        print(f"⚠️ Some API improvements needed")
        
    elif metadata_success:
        print(f"👍 GOOD: Metadata is complete but Gemini utilization is low")
        print(f"⚠️ Check Gemini configuration")
        
    else:
        print(f"❌ NEEDS WORK: Both chat and metadata need improvement")
        print(f"🔧 Review Gemini integration and API responses")

if __name__ == "__main__":
    main()
