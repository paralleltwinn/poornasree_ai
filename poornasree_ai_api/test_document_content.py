#!/usr/bin/env python3
"""
Verify responses are actually based on document content
"""
import requests
import json

def test_document_specific_responses():
    """Test that responses are actually based on document content"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Document-Specific Responses")
    print("=" * 50)
    
    # Test with very specific question that should only be answerable from our test document
    test_questions = [
        "What are the exact initialization steps?",
        "How long does initialization take?",
        "What button should I use to home all axes?",
        "Tell me about the Home button functionality",
        "What program file should I load?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/chat",
                json={
                    "user_id": "test_user",
                    "message": question
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "No response")
                confidence = data.get("confidence", 0)
                sources = data.get("sources", [])
                
                print(f"   Confidence: {confidence}")
                print(f"   Sources: {len(sources)} documents")
                print(f"   Answer: {answer[:200]}...")
                
                # Check if response contains specific content from our test document
                document_keywords = ["initialization", "30 seconds", "HOME button", "axes", "program file"]
                found_keywords = [kw for kw in document_keywords if kw.lower() in answer.lower()]
                
                if found_keywords:
                    print(f"   ✅ Found document-specific content: {found_keywords}")
                else:
                    print(f"   ⚠️  No specific document content detected")
                    
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_document_specific_responses()
