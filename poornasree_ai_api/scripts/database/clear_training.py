#!/usr/bin/env python3
"""
Clear all training data from Poornasree AI service
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.ai_service import AIService

async def clear_all_training_data():
    """Clear all training data from the AI service"""
    print("🗑️ Clearing All Training Data from Poornasree AI")
    print("=" * 50)
    
    try:
        # Initialize AI service
        print("1. Initializing AI service...")
        ai_service = AIService()
        await ai_service.initialize()
        print("   ✅ AI service initialized")
        
        # Check current status
        print("\n2. Checking current training data...")
        status = ai_service.get_status()
        document_count = status.get('document_count', 0)
        total_chunks = status.get('total_chunks', 0)
        kb_size = status.get('knowledge_base_size_mb', 0)
        
        print(f"   📊 Documents: {document_count}")
        print(f"   📊 Total Chunks: {total_chunks}")
        print(f"   📊 Knowledge Base Size: {kb_size} MB")
        
        if document_count > 0 or kb_size > 0:
            print("\n3. Clearing training data...")
            result = ai_service.clear_training_data()
            
            print("   ✅ Training data cleared successfully!")
            print(f"   📝 {result['message']}")
            print(f"   🗂️ Cleared Documents: {result['cleared_documents']}")
            print(f"   📄 Cleared Chunks: {result['cleared_chunks']}")
            print(f"   🕒 Timestamp: {result['timestamp']}")
            
            # Verify clearing
            print("\n4. Verifying data removal...")
            new_status = ai_service.get_status()
            new_document_count = new_status.get('document_count', 0)
            new_kb_size = new_status.get('knowledge_base_size_mb', 0)
            
            print(f"   📊 Documents After: {new_document_count}")
            print(f"   📊 Knowledge Base Size After: {new_kb_size} MB")
            
            if new_document_count == 0 and new_kb_size == 0:
                print("   ✅ All training data successfully removed!")
            else:
                print("   ⚠️ Some data may still remain")
                
        else:
            print("\n✅ No training data found to clear")
            print("   The AI service is already clean!")
        
        print("\n🎉 Operation completed!")
        
    except Exception as e:
        print(f"\n❌ Error during training data clearing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_all_training_data())
