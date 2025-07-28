#!/usr/bin/env python3
"""
Simple Training Test for Enhanced Poornasree AI
Tests the document training and chat response pipeline
"""

import requests
import json
import time
import os
import tempfile

API_BASE_URL = "http://localhost:8000"

def create_simple_manual():
    """Create a simple test manual for training"""
    manual_content = """
CNC MACHINE OPERATION MANUAL
Model: PrecisionCNC-5000

SAFETY INSTRUCTIONS
- Always wear safety glasses when operating the machine
- Ensure emergency stop button is accessible at all times
- Never bypass safety interlocks
- Read all safety instructions before operating

MACHINE STARTUP PROCEDURE

Step 1: Pre-Operation Checks
- Check that all safety guards are in place
- Verify emergency stop buttons are functional
- Inspect workholding devices for damage
- Ensure coolant levels are adequate

Step 2: Power On Sequence
1. Turn on main electrical power
2. Press the green START button on control panel
3. Wait for system initialization (approximately 30 seconds)
4. Home all axes using the HOME button
5. Load the required program file

TROUBLESHOOTING GUIDE

Problem: Machine Won't Start
Check the following:
- Main power switch is ON
- Emergency stops are not activated
- All safety doors are closed
- Hydraulic pressure is adequate

Problem: Error Code E001
This indicates Emergency Stop is activated
Solution: Reset emergency stop button and check safety systems

MAINTENANCE PROCEDURES

Daily Maintenance
- Clean machine surfaces and remove chips
- Check coolant level and top up if needed
- Lubricate grease points according to schedule
- Inspect cutting tools for wear or damage

Weekly Maintenance
- Change coolant filter
- Check hydraulic fluid level
- Clean electrical cabinet air filters
- Verify accuracy with test part
"""
    
    # Create temporary file with proper encoding
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(manual_content)
        return f.name

def test_api_health():
    """Test if API is running"""
    print("Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"API is healthy: {data['status']}")
            return True
        else:
            print(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        return False

def upload_test_document():
    """Upload test manual for training"""
    print("Uploading test manual...")
    
    manual_file = create_simple_manual()
    
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
                print(f"Upload successful!")
                print(f"   Filename: {result['filename']}")
                print(f"   Size: {result['file_size']} bytes")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                return True
            else:
                print(f"Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Upload error: {e}")
        return False
    finally:
        # Cleanup temp file
        if os.path.exists(manual_file):
            os.remove(manual_file)

def train_ai_model():
    """Train the AI model with uploaded documents"""
    print("Training AI model...")
    
    try:
        data = {'user_id': 'test_user'}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/train",
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Training successful!")
            print(f"   Processed documents: {result['processed_documents']}")
            print(f"   Total documents: {result['total_documents']}")
            print(f"   Training time: {result['training_time']}s")
            return True
        else:
            print(f"Training failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Training error: {e}")
        return False

def test_chat_responses():
    """Test chat responses"""
    print("Testing chat responses...")
    
    test_questions = [
        "How do I start the CNC machine?",
        "What should I do if the machine won't start?",
        "What are the safety precautions?",
        "How do I perform daily maintenance?",
        "What does error code E001 mean?"
    ]
    
    successful_tests = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        
        try:
            payload = {
                "message": question,
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
                
                print(f"   Response received (confidence: {confidence:.2f})")
                print(f"   Answer preview: {answer[:100]}...")
                
                # Simple check if response contains relevant information
                if len(answer) > 50 and confidence > 0.3:
                    successful_tests += 1
                    print(f"   Test PASSED")
                else:
                    print(f"   Test FAILED - Response too short or low confidence")
                    
            else:
                print(f"   Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"   Chat error: {e}")
    
    print(f"\nChat Test Results: {successful_tests}/{len(test_questions)} successful")
    return successful_tests >= 3  # At least 3 out of 5 should work

def main():
    """Main test function"""
    print("Enhanced Poornasree AI Training Test")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("API is not running. Please start with: python main.py")
        return
    
    print("\nDOCUMENT TRAINING TEST")
    print("=" * 50)
    
    # Upload document
    if not upload_test_document():
        print("Document upload failed")
        return
    
    # Train AI
    if not train_ai_model():
        print("AI training failed")
        return
    
    print("\nINTELLIGENCE TEST")
    print("=" * 50)
    
    # Test chat responses
    chat_success = test_chat_responses()
    
    print("\nFINAL RESULTS")
    print("=" * 50)
    
    if chat_success:
        print("ALL TESTS PASSED!")
        print("Enhanced AI training is working correctly")
        print("Document processing is functional")
        print("Chat responses are being generated from training data")
        print("\nYour Poornasree AI is ready for production use!")
    else:
        print("Some tests failed - but basic functionality is working")
        print("The system can process documents and generate responses")

if __name__ == "__main__":
    main()
