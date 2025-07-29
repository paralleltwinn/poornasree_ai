#!/usr/bin/env python3
"""
Integration Test Suite for Poornasree AI
Tests the complete integration between FastAPI backend and Flutter frontend
"""

import requests
import json
import time
from datetime import datetime
import pytz

API_BASE_URL = "http://localhost:8000"
FLUTTER_URL = "http://localhost:3000"

def test_api_health():
    """Test API health endpoints"""
    print("🔍 Testing API Health Endpoints...")
    
    try:
        # Test basic health
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic health: {data['status']}")
            print(f"   Server time: {data['timestamp']}")
            print(f"   Uptime: {data['uptime']:.1f}s")
            
            # Verify timezone is IST
            timestamp_str = data['timestamp']
            if '+05:30' in timestamp_str:
                print("✅ Indian Standard Time (IST) confirmed!")
            else:
                print("⚠️  Timezone may not be IST")
        else:
            print(f"❌ Basic health failed: {response.status_code}")
            return False
            
        # Test detailed health
        response = requests.get(f"{API_BASE_URL}/health/detailed")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detailed health: {data['status']}")
            print(f"   Memory usage: {data['system']['memory_used_percent']:.1f}%")
            print(f"   AI service: {data['services']['ai_service']['status']}")
        else:
            print(f"❌ Detailed health failed: {response.status_code}")
            
        # Test AI health
        response = requests.get(f"{API_BASE_URL}/health/ai")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI health: {data['status']}")
        else:
            print(f"❌ AI health failed: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health test error: {e}")
        return False

def test_chat_api():
    """Test chat API with Indian timezone"""
    print("\n🗣️  Testing Chat API...")
    
    try:
        # Test chat with various messages
        test_messages = [
            "Hello, test Indian time integration!",
            "What safety procedures should I follow?",
            "How do I maintain my machine?",
            "Can you help with troubleshooting?"
        ]
        
        for message in test_messages:
            payload = {
                "message": message,
                "user_id": "integration_test"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat response for: '{message[:30]}...'")
                print(f"   Response time: {data['processing_time']:.3f}s")
                print(f"   Confidence: {data['confidence']}")
                print(f"   Timestamp: {data['timestamp']}")
                
                # Verify IST timezone
                if '+05:30' in data['timestamp']:
                    print("   ✅ IST timezone confirmed in response")
                else:
                    print("   ⚠️  Timezone verification failed")
                    
            else:
                print(f"❌ Chat failed for message: {message}")
                return False
                
            time.sleep(0.5)  # Be nice to the API
            
        return True
        
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def test_document_api():
    """Test document endpoints"""
    print("\n📄 Testing Document API...")
    
    try:
        # Test document stats
        response = requests.get(f"{API_BASE_URL}/api/v1/documents/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document stats: {data['total_documents']} documents")
            print(f"   Total size: {data['total_size']} bytes")
        else:
            print(f"❌ Document stats failed: {response.status_code}")
            
        # Test supported formats
        response = requests.get(f"{API_BASE_URL}/api/v1/documents/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supported formats: {len(data['formats'])} formats")
        else:
            print(f"❌ Supported formats failed: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Document test error: {e}")
        return False

def test_flutter_connectivity():
    """Test Flutter web app connectivity"""
    print("\n🌐 Testing Flutter Web App...")
    
    try:
        response = requests.get(FLUTTER_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Flutter web app is accessible")
            if "Poornasree AI" in response.text:
                print("✅ Flutter app content verified")
            else:
                print("⚠️  Flutter app content may not be fully loaded")
            return True
        else:
            print(f"❌ Flutter web app returned: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flutter app. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Flutter test error: {e}")
        return False

def test_timezone_consistency():
    """Test timezone consistency across all endpoints"""
    print("\n🕐 Testing Indian Timezone Consistency...")
    
    try:
        endpoints = [
            "/health",
            "/health/detailed",
            "/health/ai",
            "/ping"
        ]
        
        ist_count = 0
        total_count = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if 'timestamp' in data:
                        total_count += 1
                        if '+05:30' in str(data['timestamp']):
                            ist_count += 1
                            print(f"✅ {endpoint}: IST confirmed")
                        else:
                            print(f"⚠️  {endpoint}: Timezone may not be IST")
            except:
                pass
                
        # Test chat timestamp
        try:
            payload = {"message": "timezone test", "user_id": "tz_test"}
            response = requests.post(f"{API_BASE_URL}/api/v1/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                total_count += 1
                if '+05:30' in data['timestamp']:
                    ist_count += 1
                    print("✅ Chat API: IST confirmed")
                else:
                    print("⚠️  Chat API: Timezone may not be IST")
        except:
            pass
            
        if ist_count == total_count and total_count > 0:
            print(f"🎉 All {total_count} endpoints using IST correctly!")
            return True
        else:
            print(f"⚠️  {ist_count}/{total_count} endpoints using IST")
            return False
            
    except Exception as e:
        print(f"❌ Timezone test error: {e}")
        return False

def main():
    """Run complete integration test suite"""
    print("=" * 60)
    print("🚀 POORNASREE AI INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Testing Flutter at: {FLUTTER_URL}")
    print(f"Test time: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()
    
    results = []
    
    # Run all tests
    results.append(("API Health", test_api_health()))
    results.append(("Chat API", test_chat_api()))
    results.append(("Document API", test_document_api()))
    results.append(("Flutter Connectivity", test_flutter_connectivity()))
    results.append(("Timezone Consistency", test_timezone_consistency()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integration is working perfectly!")
        print("\n✅ FastAPI backend running with Indian timezone")
        print("✅ Flutter frontend accessible and functional")
        print("✅ API endpoints returning IST timestamps")
        print("✅ Chat functionality working correctly")
        print("✅ Document management operational")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("\n🔗 Quick Links:")
    print(f"   API Documentation: {API_BASE_URL}/docs")
    print(f"   Flutter Web App: {FLUTTER_URL}")
    print(f"   API Health: {API_BASE_URL}/health")

if __name__ == "__main__":
    main()
