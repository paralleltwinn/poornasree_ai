#!/usr/bin/env python3
"""
Debug PDF text extraction to see what content is being extracted
"""
import sys
sys.path.append('.')

from app.services.document_service import DocumentService
import asyncio

async def debug_pdf_extraction():
    """Debug what text is being extracted from the enhanced PDF"""
    doc_service = DocumentService()
    pdf_file = "enhanced_cnc_manual.pdf"
    
    print("🔍 PDF TEXT EXTRACTION DEBUG")
    print("=" * 50)
    
    try:
        # Extract text using our service
        result = await doc_service.extract_text_from_file(pdf_file)
        
        if result["status"] == "success":
            extracted_text = result["text"]
            print(f"✅ Extraction successful!")
            print(f"📄 Text length: {len(extracted_text)} characters")
            print(f"📄 Word count: {result['word_count']} words")
            
            print(f"\n📝 EXTRACTED CONTENT PREVIEW:")
            print("=" * 50)
            print(extracted_text[:2000])  # First 2000 characters
            print("...")
            print(f"\n📝 LAST 500 CHARACTERS:")
            print("=" * 30)
            print(extracted_text[-500:])
            
            # Check for specific content
            print(f"\n🔍 CONTENT ANALYSIS:")
            print("=" * 30)
            
            search_terms = [
                "PMC-2000", "12000", "RPM", "15", "kW", "45 seconds",
                "safety glasses", "E100", "spindle overheat", "24 tools",
                "±0.005", "40 hours", "lubricate", "ball screws"
            ]
            
            for term in search_terms:
                found = term.lower() in extracted_text.lower()
                status = "✅" if found else "❌"
                print(f"   {status} '{term}': {found}")
                
        else:
            print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_pdf_extraction())
