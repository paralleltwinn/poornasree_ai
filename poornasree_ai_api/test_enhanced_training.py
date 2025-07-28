#!/usr/bin/env python3
"""
Production Training Test for Enhanced Poornasree AI
Tests the complete document training and chat response pipeline
"""

import requests
import json
import time
import os
from pathlib import Path
import tempfile

API_BASE_URL = "http://localhost:8000"

def create_test_manual():
    """Create a comprehensive test manual for training"""
    manual_content = """
ADVANCED CNC MACHINE OPERATION MANUAL
Model: PrecisionCNC-5000 Series
Version: 2.0

## SAFETY INSTRUCTIONS

⚠️ WARNING: Always wear safety glasses when operating the machine
⚠️ CAUTION: Ensure emergency stop button is accessible at all times
⚠️ DANGER: Never bypass safety interlocks
⚠️ IMPORTANT: Read all safety instructions before operating

## MACHINE STARTUP PROCEDURE

### Step 1: Pre-Operation Checks
• Check that all safety guards are in place
• Verify emergency stop buttons are functional
• Inspect workholding devices for damage
• Ensure coolant levels are adequate

### Step 2: Power On Sequence
1. Turn on main electrical power
2. Press the green START button on control panel
3. Wait for system initialization (approximately 30 seconds)
4. Home all axes using the HOME button
5. Load the required program file

### Step 3: Tool Setup
• Install appropriate cutting tools
• Set tool length offsets
• Verify tool condition before use
• Update tool library in control system

## OPERATION PROCEDURES

### Programming Mode
To enter programming mode:
1. Press PROG button on control panel
2. Select NEW PROGRAM from menu
3. Enter program number (1001-9999)
4. Input G-code commands
5. Verify syntax before execution

### Automatic Operation
For automatic machining:
1. Load workpiece securely in fixture
2. Set work coordinate system (G54-G59)
3. Run program in simulation mode first
4. Start automatic cycle with CYCLE START
5. Monitor operation continuously

### Manual Operation
For manual positioning:
• Use JOG mode for axis movement
• Select appropriate feed rate (1-100%)
• Move axes using directional buttons
• Use handwheel for precise positioning

## MAINTENANCE PROCEDURES

### Daily Maintenance
🔧 Clean machine surfaces and remove chips
🔧 Check coolant level and top up if needed
🔧 Lubricate grease points according to schedule
🔧 Inspect cutting tools for wear or damage

### Weekly Maintenance
🔧 Change coolant filter
🔧 Check hydraulic fluid level
🔧 Clean electrical cabinet air filters
🔧 Verify accuracy with test part

### Monthly Maintenance
🔧 Replace spindle oil
🔧 Check way cover condition
🔧 Inspect cable carriers for wear
🔧 Update machine hour counter

## TROUBLESHOOTING GUIDE

### Problem: Machine Won't Start
Check the following:
• Main power switch is ON
• Emergency stops are not activated
• All safety doors are closed
• Hydraulic pressure is adequate

### Problem: Excessive Tool Wear
Possible causes:
• Incorrect cutting speeds/feeds
• Poor coolant flow
• Workpiece material harder than expected
• Tool geometry not optimized

### Problem: Poor Surface Finish
Troubleshooting steps:
• Reduce feed rate
• Check tool sharpness
• Verify workholding rigidity
• Adjust spindle speed

### Problem: Dimensional Accuracy Issues
Investigation checklist:
• Check tool wear and replace if needed
• Verify work coordinate system setup
• Inspect machine for wear in slides
• Review thermal compensation settings

## SPECIFICATIONS

### Machine Capacity
- X-axis travel: 1000mm
- Y-axis travel: 500mm  
- Z-axis travel: 500mm
- Maximum workpiece weight: 500kg
- Spindle speed range: 50-8000 RPM

### Power Requirements
- Main motor: 15kW
- Spindle motor: 7.5kW
- Hydraulic pump: 3kW
- Total power consumption: 30kW

### Accuracy Specifications
- Positioning accuracy: ±0.005mm
- Repeatability: ±0.003mm
- Surface finish capability: Ra 0.8μm

## ERROR CODES

### E001: Emergency Stop Activated
Reset emergency stop button and check safety systems

### E002: Servo Drive Fault
Check servo motor connections and feedback cables

### E003: Spindle Overload
Reduce cutting parameters or check for mechanical binding

### E004: Hydraulic Pressure Low
Check hydraulic fluid level and pump operation

### E005: Tool Magazine Error
Inspect tool changer mechanism and retry operation

## APPENDIX

### Recommended Cutting Parameters
For Steel (HRC 30-40):
- Speed: 200-400 RPM
- Feed: 0.1-0.3 mm/rev
- Depth: 1-3mm

For Aluminum:
- Speed: 800-2000 RPM  
- Feed: 0.2-0.5 mm/rev
- Depth: 2-5mm

### Contact Information
Technical Support: 1-800-CNC-HELP
Email: support@precisioncnc.com
Website: www.precisioncnc.com/support
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(manual_content)
        return f.name

def test_api_health():
    """Test if API is running and healthy"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data['status']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_ai_service_status():
    """Test AI service status"""
    print("🤖 Testing AI Service Status...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/ai", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service Status: {data['status']}")
            print(f"   Model: {data.get('ai_service', {}).get('model_name', 'unknown')}")
            print(f"   Documents: {data.get('ai_service', {}).get('document_count', 0)}")
            print(f"   Embeddings: {data.get('ai_service', {}).get('embeddings_available', False)}")
            return True
        else:
            print(f"❌ AI service check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI service test error: {e}")
        return False

def upload_test_document():
    """Upload test manual for training"""
    print("📄 Uploading test manual...")
    
    manual_file = create_test_manual()
    
    try:
        with open(manual_file, 'rb') as f:
            files = {
                'file': ('test_cnc_manual.txt', f, 'text/plain')
            }
            data = {
                'description': 'Test CNC machine manual for AI training',
                'user_id': 'test_user'
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/documents/upload", 
                files=files, 
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful:")
                print(f"   Filename: {result['filename']}")
                print(f"   Size: {result['file_size']} bytes")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                print(f"   Chunks: {result.get('processed_chunks', 0)}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Cleanup temp file
        if os.path.exists(manual_file):
            os.remove(manual_file)

def train_ai_model():
    """Train the AI model with uploaded documents"""
    print("🧠 Training AI model...")
    
    try:
        data = {'user_id': 'test_user'}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/train",
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Training successful:")
            print(f"   Processed documents: {result['processed_documents']}")
            print(f"   Total documents: {result['total_documents']}")
            print(f"   Training time: {result['training_time']}s")
            
            ai_status = result.get('ai_status', {})
            print(f"   AI documents: {ai_status.get('document_count', 0)}")
            print(f"   AI chunks: {ai_status.get('total_chunks', 0)}")
            return True
        else:
            print(f"❌ Training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False

def test_chat_responses():
    """Test various chat scenarios"""
    print("💬 Testing chat responses...")
    
    test_questions = [
        {
            "question": "How do I start the CNC machine?",
            "expected_topics": ["startup", "power", "procedure", "button"]
        },
        {
            "question": "What should I do if the machine won't start?",
            "expected_topics": ["troubleshoot", "power", "emergency", "safety"]
        },
        {
            "question": "What are the safety precautions?",
            "expected_topics": ["safety", "warning", "glasses", "emergency"]
        },
        {
            "question": "How do I perform daily maintenance?",
            "expected_topics": ["maintenance", "daily", "clean", "lubricate"]
        },
        {
            "question": "What does error code E001 mean?",
            "expected_topics": ["E001", "emergency", "stop", "reset"]
        }
    ]
    
    successful_tests = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n🔸 Test {i}: {test['question']}")
        
        try:
            payload = {
                "message": test["question"],
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['response']
                confidence = data['confidence']
                sources = data.get('source_documents', [])
                
                print(f"   ✅ Response received (confidence: {confidence:.2f})")
                print(f"   📝 Answer preview: {answer[:150]}...")
                print(f"   📚 Sources: {len(sources)} document(s)")
                
                # Check if response contains expected topics
                answer_lower = answer.lower()
                found_topics = [topic for topic in test['expected_topics'] 
                              if topic in answer_lower]
                
                if found_topics:
                    print(f"   🎯 Found relevant topics: {', '.join(found_topics)}")
                    successful_tests += 1
                else:
                    print(f"   ⚠️ Expected topics not found in response")
                    
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
    
    print(f"\n📊 Chat Test Results: {successful_tests}/{len(test_questions)} successful")
    return successful_tests == len(test_questions)

def test_document_search():
    """Test document search functionality"""
    print("🔍 Testing document search...")
    
    try:
        payload = {
            "query": "safety procedures",
            "limit": 5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Search successful: {len(results)} results found")
            
            for i, result in enumerate(results[:3], 1):
                score = result.get('score', 0)
                snippet = result.get('text', '')[:100]
                print(f"   {i}. Score: {score:.3f} - {snippet}...")
            
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced Poornasree AI Training Test")
    print("=" * 60)
    
    # Test API health
    if not test_api_health():
        print("❌ API is not running. Please start with: python main.py")
        return
    
    # Test AI service
    if not test_ai_service_status():
        print("❌ AI service is not ready")
        return
    
    print("\n" + "=" * 60)
    print("📚 DOCUMENT TRAINING TEST")
    print("=" * 60)
    
    # Upload document
    if not upload_test_document():
        print("❌ Document upload failed")
        return
    
    # Train AI
    if not train_ai_model():
        print("❌ AI training failed")
        return
    
    print("\n" + "=" * 60)
    print("🧠 INTELLIGENCE TEST")
    print("=" * 60)
    
    # Test chat responses
    chat_success = test_chat_responses()
    
    # Test search
    search_success = test_document_search()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS")
    print("=" * 60)
    
    if chat_success and search_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced AI training is working perfectly")
        print("✅ Document processing is production-ready")
        print("✅ Chat responses are intelligent and context-aware")
        print("✅ Search functionality is operational")
        print("\n🚀 Your Poornasree AI is ready for production use!")
    else:
        print("⚠️ Some tests failed - check the logs above")
        print("📝 The system may still work but with reduced functionality")

if __name__ == "__main__":
    main()
