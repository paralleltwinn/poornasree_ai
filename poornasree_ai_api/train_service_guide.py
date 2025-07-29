import asyncio
import pandas as pd
import os
from typing import Dict, List, Optional
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

class ServiceGuideTrainer:
    """Enhanced trainer for service guide Excel files with row-wise processing"""
    
    def __init__(self):
        self.document_service = DocumentService()
        self.ai_service = AIService()
        self.service_data = []
        
    async def train_service_guide_excel(self, file_path: str) -> Dict:
        """Train Excel file as service guide with row-wise processing"""
        print(f"🔄 Training service guide from Excel: {file_path}")
        
        try:
            # Extract row-wise data
            service_entries = await self._extract_service_entries(file_path)
            
            if not service_entries:
                return {"success": False, "message": "No service entries found"}
            
            # Process each service entry with Gemini
            trained_entries = []
            for i, entry in enumerate(service_entries):
                print(f"📋 Processing service entry {i+1}/{len(service_entries)}")
                
                # Create structured prompt for Gemini
                structured_entry = await self._structure_service_entry(entry)
                trained_entries.append(structured_entry)
                
                # Add to knowledge base
                await self._add_to_knowledge_base(structured_entry)
            
            result = {
                "success": True,
                "entries_processed": len(trained_entries),
                "file": file_path,
                "service_guide_data": trained_entries[:5]  # Sample first 5
            }
            
            print(f"✅ Service guide training complete: {len(trained_entries)} entries processed")
            return result
            
        except Exception as e:
            logger.error(f"Error training service guide: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_service_entries(self, file_path: str) -> List[Dict]:
        """Extract service entries row by row from Excel"""
        try:
            # Read Excel file with pandas for better row control
            df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
            
            service_entries = []
            
            for sheet_name, sheet_df in df.items():
                print(f"📊 Processing sheet: {sheet_name}")
                
                # Clean the dataframe
                sheet_df = sheet_df.dropna(how='all')  # Remove empty rows
                sheet_df = sheet_df.fillna('')  # Fill NaN with empty string
                
                # Get column headers
                headers = [str(col).strip() for col in sheet_df.columns]
                
                # Process each row as a service entry
                for index, row in sheet_df.iterrows():
                    entry = {
                        "sheet": sheet_name,
                        "row_number": index + 2,  # +2 because pandas is 0-indexed and Excel has headers
                        "data": {}
                    }
                    
                    # Map each column to its value
                    for col_idx, header in enumerate(headers):
                        value = str(row.iloc[col_idx]).strip() if col_idx < len(row) else ""
                        if value and value != 'nan':
                            entry["data"][header] = value
                    
                    # Only add entries with actual data
                    if entry["data"] and any(v.strip() for v in entry["data"].values()):
                        service_entries.append(entry)
            
            print(f"📋 Extracted {len(service_entries)} service entries")
            return service_entries
            
        except Exception as e:
            logger.error(f"Error extracting service entries: {e}")
            return []
    
    async def _structure_service_entry(self, entry: Dict) -> Dict:
        """Structure service entry using Gemini AI"""
        try:
            # Create a prompt for Gemini to structure the service data
            data_text = "\n".join([f"{k}: {v}" for k, v in entry["data"].items()])
            
            prompt = f"""
            You are analyzing a service guide entry. Please structure this data into a clear service guide format:
            
            Raw Data:
            {data_text}
            
            Please provide a structured response with:
            1. Service Title/Name
            2. Service Description  
            3. Steps/Procedures
            4. Requirements/Prerequisites
            5. Safety Notes (if any)
            6. Additional Information
            
            Make it practical and useful for technicians.
            """
            
            # Get AI response using chat method
            ai_result = await self.ai_service.chat(prompt)
            ai_response = ai_result.get('response', 'Error processing with AI')
            
            structured_entry = {
                "original_row": entry["row_number"],
                "sheet": entry["sheet"],
                "raw_data": entry["data"],
                "structured_content": ai_response,
                "search_keywords": self._extract_keywords(entry["data"]),
                "category": self._determine_category(entry["data"])
            }
            
            return structured_entry
            
        except Exception as e:
            logger.error(f"Error structuring service entry: {e}")
            return {
                "original_row": entry["row_number"],
                "sheet": entry["sheet"],
                "raw_data": entry["data"],
                "structured_content": f"Error processing: {str(e)}",
                "search_keywords": [],
                "category": "unknown"
            }
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract searchable keywords from service data"""
        keywords = []
        
        for key, value in data.items():
            # Add column headers as keywords
            keywords.extend(key.lower().split())
            
            # Add significant words from values
            if isinstance(value, str) and len(value) > 3:
                words = value.lower().split()
                keywords.extend([w for w in words if len(w) > 3])
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def _determine_category(self, data: Dict) -> str:
        """Determine service category from data"""
        # Common service guide categories
        categories = {
            "maintenance": ["maintenance", "service", "check", "inspect", "clean"],
            "repair": ["repair", "fix", "replace", "troubleshoot", "problem"],
            "installation": ["install", "setup", "mount", "connect", "wire"],
            "safety": ["safety", "warning", "caution", "danger", "hazard"],
            "operation": ["operate", "run", "start", "stop", "control"],
            "parts": ["part", "component", "spare", "item", "number"]
        }
        
        # Combine all text from the entry
        all_text = " ".join(str(v).lower() for v in data.values())
        
        # Check which category has most matches
        best_category = "general"
        max_matches = 0
        
        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in all_text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category
    
    async def _add_to_knowledge_base(self, structured_entry: Dict):
        """Add structured entry to knowledge base for search"""
        try:
            # Create searchable content
            search_content = f"""
            Service Guide Entry (Row {structured_entry['original_row']}, Sheet: {structured_entry['sheet']})
            Category: {structured_entry['category']}
            
            {structured_entry['structured_content']}
            
            Keywords: {', '.join(structured_entry['search_keywords'])}
            """
            
            # Here you would typically add to your vector database or search index
            # For now, just log the addition
            logger.info(f"Added service entry to knowledge base: Row {structured_entry['original_row']}")
            
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {e}")

async def main():
    """Test the service guide trainer"""
    trainer = ServiceGuideTrainer()
    
    # Test with available Excel files
    excel_files = [
        "test_cnc_data.xlsx",
        "Training syllabus and documents.xlsx"
    ]
    
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"\n🔄 Training service guide from: {excel_file}")
            result = await trainer.train_service_guide_excel(excel_file)
            print(f"Result: {result.get('success', False)}")
            if result.get('success'):
                print(f"Entries processed: {result.get('entries_processed', 0)}")

if __name__ == "__main__":
    asyncio.run(main())
