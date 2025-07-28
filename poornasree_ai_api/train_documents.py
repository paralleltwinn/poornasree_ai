#!/usr/bin/env python3
"""
Test script to upload and train Poornasree AI with user manuals
"""
import requests
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

def upload_document(file_path, description="", user_id="admin"):
    """Upload a document to train the AI"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file, 'application/pdf')
            }
            data = {
                'description': description,
                'user_id': user_id
            }
            
            print(f"🔄 Uploading: {os.path.basename(file_path)}")
            response = requests.post(f"{API_BASE_URL}/api/v1/documents/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   File: {result['filename']}")
                print(f"   Size: {result['file_size']} bytes")
                print(f"   Chunks: {result['processed_chunks']}")
                print(f"   Time: {result['processing_time']:.2f}s")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return False

def test_chat(message, user_id="admin"):
    """Test chat with the trained AI"""
    try:
        data = {
            "message": message,
            "user_id": user_id
        }
        
        print(f"🗣️  Testing chat: {message}")
        response = requests.post(f"{API_BASE_URL}/api/v1/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 AI Response:")
            print(f"   {result['response']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Sources: {len(result.get('source_documents', []))} documents")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return False

def get_document_stats():
    """Get document statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/documents/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 Document Statistics:")
            print(f"   Total Documents: {stats['total_documents']}")
            print(f"   Total Size: {stats['total_size']} bytes")
            print(f"   Recent Uploads: {stats['recent_uploads']}")
            return stats
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None

def main():
    print("=== Poornasree AI Document Training Tool ===")
    print("API Server: http://localhost:8000")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API server is not running!")
            print("Please start the server with: python main.py")
            return
    except Exception:
        print("❌ Cannot connect to API server!")
        print("Please start the server with: python main.py")
        return
    
    print("✅ API server is running!")
    
    # Get current statistics
    get_document_stats()
    
    # Example manual upload (you can modify this)
    print("\n🔄 Example: Upload a sample manual...")
    
    # Create a sample manual text file for testing
    sample_manual = """
    MACHINE OPERATION MANUAL
    
    Model: CNC-3000 Series
    
    SAFETY INSTRUCTIONS:
    1. Always wear safety glasses
    2. Ensure emergency stop is accessible
    3. Check all safety guards before operation
    
    OPERATION PROCEDURE:
    1. Power on the machine using the main switch
    2. Initialize the control system
    3. Load the program file
    4. Set the workpiece coordinates
    5. Run the program in simulation mode first
    6. Start production after verification
    
    TROUBLESHOOTING:
    - If machine stops unexpectedly, check emergency stop button
    - For positioning errors, recalibrate the axes
    - Clean sensors if accuracy issues occur
    
    MAINTENANCE:
    - Daily: Clean work area and check coolant levels
    - Weekly: Lubricate moving parts
    - Monthly: Inspect electrical connections
    """
    
    # Save sample manual to file
    sample_file = "sample_manual.txt"
    with open(sample_file, 'w') as f:
        f.write(sample_manual)
    
    # Upload the sample manual
    upload_success = upload_document(
        sample_file, 
        "CNC-3000 Series Operation Manual",
        "admin"
    )
    
    if upload_success:
        print("\n🔄 Testing AI chat with uploaded manual...")
        
        # Test questions
        test_questions = [
            "How do I start the CNC machine?",
            "What safety precautions should I take?",
            "What should I do if the machine stops unexpectedly?",
            "How often should I clean the machine?"
        ]
        
        for question in test_questions:
            print(f"\n" + "="*50)
            test_chat(question)
    
    # Clean up
    if os.path.exists(sample_file):
        os.remove(sample_file)
    
    print(f"\n" + "="*50)
    print("🎉 Training test complete!")
    print("\nNext steps:")
    print("1. Upload your actual PDF manuals using this script")
    print("2. Test with real questions about your equipment")
    print("3. Use the Flutter web app for a better interface")

if __name__ == "__main__":
    main()
