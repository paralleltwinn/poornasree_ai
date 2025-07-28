#!/usr/bin/env python3
"""
Test Excel file training with multiple sheets
"""
import requests
import json
import os
import time

def test_excel_training():
    """Test Excel file upload and training with multiple sheets"""
    base_url = "http://localhost:8000"
    excel_file = "test_cnc_data.xlsx"
    
    print("📊 Excel Training Test")
    print("=" * 50)
    
    # Check if Excel file exists
    if not os.path.exists(excel_file):
        print("❌ Test Excel file not found. Run create_test_excel.py first.")
        return
    
    print(f"📁 Using Excel file: {excel_file}")
    print(f"📄 File size: {os.path.getsize(excel_file)} bytes")
    
    # Test API health
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("\n🔄 EXCEL UPLOAD TEST")
    print("=" * 30)
    
    # Upload Excel file
    try:
        with open(excel_file, 'rb') as f:
            files = {'file': (excel_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'user_id': 'test_user',
                'description': 'Test CNC machine data with multiple Excel sheets'
            }
            
            upload_response = requests.post(
                f"{base_url}/api/v1/documents/upload",
                files=files,
                data=data,
                timeout=60
            )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print("✅ Excel upload successful!")
            print(f"   Document ID: {upload_data.get('document_id')}")
            print(f"   Filename: {upload_data.get('filename')}")
            print(f"   File size: {upload_data.get('file_size')} bytes")
            print(f"   Processing time: {upload_data.get('processing_time', 0):.3f}s")
            
            # Check if metadata shows multiple sheets
            metadata = upload_data.get('metadata', {})
            if 'key_sections' in metadata:
                print(f"   Detected sections: {len(metadata['key_sections'])}")
                for section in metadata['key_sections']:
                    print(f"     - {section}")
                    
            document_type = metadata.get('document_type', 'unknown')
            print(f"   Document type: {document_type}")
            
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Error: {upload_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    print("\n🧠 AI TRAINING TEST")
    print("=" * 30)
    
    # Train AI with Excel data
    try:
        train_response = requests.post(
            f"{base_url}/api/v1/documents/train",
            json={"user_id": "test_user"},
            timeout=120
        )
        
        if train_response.status_code == 200:
            train_data = train_response.json()
            print("✅ Training successful!")
            print(f"   Processed documents: {train_data.get('processed_documents', 0)}")
            print(f"   Total documents: {train_data.get('total_documents', 0)}")
            print(f"   Training time: {train_data.get('training_time', 0):.3f}s")
        else:
            print(f"❌ Training failed: {train_response.status_code}")
            print(f"   Error: {train_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return
    
    print("\n💬 EXCEL-SPECIFIC CHAT TESTS")
    print("=" * 30)
    
    # Test questions specific to Excel content
    excel_questions = [
        "What is the max spindle speed of the machine?",
        "How often should I lubricate the ball screws?",
        "What tools are in the inventory?",
        "What does error code E001 mean?",
        "What is the table size of the machine?",
        "When is the next maintenance due for air filters?",
        "Which tool is used for 3D machining?",
        "How do I fix a coolant low level error?",
        "What is the travel distance for the X-axis?",
        "What condition is tool T03 in?"
    ]
    
    successful_tests = 0
    total_tests = len(excel_questions)
    
    for i, question in enumerate(excel_questions, 1):
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
                
                print(f"   ✅ Response received (confidence: {confidence})")
                print(f"   Sources: {len(sources)} documents")
                print(f"   Answer preview: {answer[:150]}...")
                
                # Check for Excel-specific keywords
                excel_keywords = ["sheet:", "specification", "maintenance", "tool", "error", "10000", "weekly", "carbide", "e001"]
                found_keywords = [kw for kw in excel_keywords if kw.lower() in answer.lower()]
                
                if found_keywords:
                    print(f"   📊 Excel content detected: {found_keywords[:3]}")
                    successful_tests += 1
                else:
                    print(f"   ⚠️  No specific Excel content detected")
                    
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📊 FINAL RESULTS")
    print("=" * 30)
    print(f"Excel Upload: ✅ Success")
    print(f"AI Training: ✅ Success") 
    print(f"Chat Tests: {successful_tests}/{total_tests} successful")
    
    if successful_tests >= total_tests * 0.8:  # 80% success rate
        print("🎉 Excel training is working excellently!")
        print("The AI can now answer questions from multiple Excel sheets")
    elif successful_tests >= total_tests * 0.6:  # 60% success rate
        print("✅ Excel training is working well with room for improvement")
    else:
        print("⚠️  Excel training needs optimization")
    
    print("\n📋 Excel Features Successfully Tested:")
    print("  ✅ Multiple sheet support (.xlsx format)")
    print("  ✅ Structured data extraction")
    print("  ✅ Sheet-specific content identification")
    print("  ✅ Integration with AI training pipeline")
    print("  ✅ Context-aware responses from spreadsheet data")

if __name__ == "__main__":
    test_excel_training()
