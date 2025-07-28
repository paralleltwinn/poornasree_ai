#!/usr/bin/env python3
"""
Check specific AI responses to debug what content is missing
"""
import requests
import json

def check_specific_responses():
    """Check specific AI responses to see what's being returned"""
    base_url = "http://localhost:8000"
    user_id = "test_user_optimized"
    
    print("🔍 RESPONSE CONTENT ANALYSIS")
    print("=" * 50)
    
    # Test specific questions that are failing
    failing_questions = [
        "What is the positioning accuracy?",
        "What is the tool magazine capacity?", 
        "What does error E100 indicate?",
        "What is the machine warranty period?"
    ]
    
    for question in failing_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/chat",
                json={"user_id": user_id, "message": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                confidence = data.get("confidence", 0)
                
                print(f"Confidence: {confidence}")
                print(f"Full Response:")
                print(answer)
                print()
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_specific_responses()
