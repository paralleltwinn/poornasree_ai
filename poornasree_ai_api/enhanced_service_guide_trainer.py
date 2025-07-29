import asyncio
import pandas as pd
import os
import re
from typing import Dict, List
import json
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
from pdf_accuracy_enhancer import PDFAccuracyEnhancer
import logging

logger = logging.getLogger(__name__)

class EnhancedServiceGuideTrainer:
    """Enhanced service guide trainer with direct Gemini integration"""
    
    def __init__(self):
        self.document_service = DocumentService()
        self.ai_service = AIService()
        self.accuracy_enhancer = PDFAccuracyEnhancer()
        
    async def train_excel_service_guide(self, file_path: str) -> Dict:
        """Train Excel file as service guide with row-wise Gemini processing"""
        print(f"🔄 Starting enhanced service guide training: {file_path}")
        
        try:
            # Initialize AI service
            await self.ai_service.initialize()
            
            # Extract Excel data row by row
            service_entries = await self._extract_excel_service_data(file_path)
            
            if not service_entries:
                return {"success": False, "message": "No service data found"}
            
            # Process each entry with structured training
            trained_entries = []
            knowledge_base_entries = []
            
            for i, entry in enumerate(service_entries):
                print(f"📋 Training service entry {i+1}/{len(service_entries)}")
                
                # Create structured service documentation
                service_doc = await self._create_service_documentation(entry)
                trained_entries.append(service_doc)
                
                # Add to AI knowledge base
                knowledge_entry = await self._add_to_ai_knowledge_base(service_doc)
                knowledge_base_entries.append(knowledge_entry)
            
            # Save training results
            await self._save_training_results(file_path, trained_entries)
            
            result = {
                "success": True,
                "file": file_path,
                "entries_trained": len(trained_entries),
                "knowledge_base_entries": len(knowledge_base_entries),
                "sample_entries": trained_entries[:3],
                "training_summary": self._create_training_summary(trained_entries)
            }
            
            print(f"✅ Service guide training complete!")
            print(f"   📊 Entries trained: {len(trained_entries)}")
            print(f"   🧠 Knowledge base entries: {len(knowledge_base_entries)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced training error: {e}")
            return {"success": False, "error": str(e)}
    
    async def train_pdf_service_guide(self, file_path: str) -> Dict:
        """Train PDF file as service guide with structured section processing"""
        print(f"🔄 Starting enhanced PDF service guide training: {file_path}")
        
        try:
            # Initialize AI service
            await self.ai_service.initialize()
            
            # Extract PDF data section by section
            service_entries = await self._extract_pdf_service_data(file_path)
            
            if not service_entries:
                return {"success": False, "message": "No PDF service data found"}
            
            # Process each entry with structured training
            trained_entries = []
            knowledge_base_entries = []
            
            for i, entry in enumerate(service_entries):
                print(f"📋 Training PDF service entry {i+1}/{len(service_entries)}")
                
                # Create structured service documentation
                service_doc = await self._create_pdf_service_documentation(entry)
                trained_entries.append(service_doc)
                
                # Add to AI knowledge base
                knowledge_entry = await self._add_pdf_to_ai_knowledge_base(service_doc)
                knowledge_base_entries.append(knowledge_entry)
            
            # Save training results
            await self._save_training_results(file_path, trained_entries)
            
            result = {
                "success": True,
                "file": file_path,
                "entries_trained": len(trained_entries),
                "knowledge_base_entries": len(knowledge_base_entries),
                "sample_entries": trained_entries[:3],
                "training_summary": self._create_training_summary(trained_entries)
            }
            
            print(f"✅ Service guide training complete!")
            print(f"   📊 Entries trained: {len(trained_entries)}")
            print(f"   🧠 Knowledge base entries: {len(knowledge_base_entries)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced training error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_excel_service_data(self, file_path: str) -> List[Dict]:
        """Extract service data from Excel file"""
        try:
            # Use pandas to read Excel file
            excel_data = pd.read_excel(file_path, sheet_name=None)
            service_entries = []
            
            for sheet_name, df in excel_data.items():
                print(f"📊 Processing sheet: {sheet_name}")
                
                # Clean and process dataframe
                df = df.dropna(how='all').fillna('')
                
                # Get column headers
                headers = [str(col).strip() for col in df.columns]
                
                # Process each row
                for idx, row in df.iterrows():
                    row_data = {}
                    for col_idx, header in enumerate(headers):
                        if col_idx < len(row):
                            value = str(row.iloc[col_idx]).strip()
                            if value and value != 'nan':
                                row_data[header] = value
                    
                    if row_data:  # Only process rows with data
                        service_entry = {
                            "sheet": sheet_name,
                            "row": idx + 2,  # Excel row number
                            "data": row_data,
                            "entry_id": f"{sheet_name}_row_{idx+2}"
                        }
                        service_entries.append(service_entry)
            
            print(f"📋 Extracted {len(service_entries)} service entries")
            return service_entries
            
        except Exception as e:
            logger.error(f"Error extracting Excel data: {e}")
            return []
    
    async def _create_service_documentation(self, entry: Dict) -> Dict:
        """Create structured service documentation"""
        try:
            # Format the raw data for documentation
            data_summary = self._format_entry_data(entry["data"])
            
            # Determine entry type and category
            entry_type = self._classify_service_entry(entry)
            
            # Create structured documentation
            service_doc = {
                "id": entry["entry_id"],
                "sheet": entry["sheet"],
                "row": entry["row"],
                "type": entry_type["type"],
                "category": entry_type["category"],
                "title": self._generate_title(entry["data"]),
                "description": self._generate_description(entry["data"], entry_type),
                "details": data_summary,
                "keywords": self._extract_keywords(entry["data"]),
                "searchable_content": self._create_searchable_content(entry["data"]),
                "raw_data": entry["data"]
            }
            
            return service_doc
            
        except Exception as e:
            logger.error(f"Error creating service documentation: {e}")
            return {
                "id": entry.get("entry_id", "unknown"),
                "error": str(e),
                "raw_data": entry.get("data", {})
            }
    
    def _format_entry_data(self, data: Dict) -> str:
        """Format entry data into readable text"""
        formatted_lines = []
        for key, value in data.items():
            formatted_lines.append(f"{key}: {value}")
        return "\n".join(formatted_lines)
    
    def _classify_service_entry(self, entry: Dict) -> Dict:
        """Classify the type and category of service entry"""
        sheet = entry["sheet"].lower()
        data_text = " ".join(str(v).lower() for v in entry["data"].values())
        
        # Determine type based on sheet name
        if "specification" in sheet:
            entry_type = "specification"
        elif "maintenance" in sheet:
            entry_type = "maintenance"
        elif "tool" in sheet or "inventory" in sheet:
            entry_type = "tool"
        elif "error" in sheet or "code" in sheet:
            entry_type = "troubleshooting"
        else:
            entry_type = "general"
        
        # Determine category based on content
        categories = {
            "safety": ["safety", "warning", "caution", "danger"],
            "maintenance": ["maintenance", "service", "check", "clean", "replace"],
            "operation": ["operate", "run", "start", "stop", "control"],
            "specification": ["spec", "parameter", "value", "limit", "range"],
            "troubleshooting": ["error", "fault", "problem", "issue", "fix"]
        }
        
        category = "general"
        for cat_name, keywords in categories.items():
            if any(keyword in data_text for keyword in keywords):
                category = cat_name
                break
        
        return {"type": entry_type, "category": category}
    
    def _generate_title(self, data: Dict) -> str:
        """Generate a title for the service entry"""
        # Look for title-like fields
        title_fields = ["title", "name", "description", "parameter", "item"]
        
        for field in title_fields:
            for key, value in data.items():
                if field.lower() in key.lower() and value:
                    return f"{key}: {value}"
        
        # Fallback: use first meaningful field
        for key, value in data.items():
            if value and len(str(value)) > 3:
                return f"{key}: {value}"
        
        return "Service Entry"
    
    def _generate_description(self, data: Dict, entry_type: Dict) -> str:
        """Generate description based on entry type"""
        description_parts = []
        
        if entry_type["type"] == "specification":
            description_parts.append("Technical specification entry")
        elif entry_type["type"] == "maintenance":
            description_parts.append("Maintenance procedure entry")
        elif entry_type["type"] == "tool":
            description_parts.append("Tool or equipment entry")
        elif entry_type["type"] == "troubleshooting":
            description_parts.append("Troubleshooting guide entry")
        else:
            description_parts.append("Service guide entry")
        
        # Add category info
        description_parts.append(f"Category: {entry_type['category']}")
        
        # Add data summary
        field_count = len([v for v in data.values() if v])
        description_parts.append(f"Contains {field_count} data fields")
        
        return " | ".join(description_parts)
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract searchable keywords"""
        keywords = set()
        
        for key, value in data.items():
            # Add field names as keywords
            keywords.update(key.lower().split())
            
            # Add significant words from values
            if isinstance(value, str):
                words = value.lower().split()
                keywords.update([w for w in words if len(w) > 2])
        
        return list(keywords)
    
    def _create_searchable_content(self, data: Dict) -> str:
        """Create searchable content string"""
        content_parts = []
        
        for key, value in data.items():
            content_parts.append(f"{key} {value}")
        
        return " ".join(content_parts)
    
    async def _add_to_ai_knowledge_base(self, service_doc: Dict) -> bool:
        """Add service documentation to AI knowledge base"""
        try:
            # Create training text
            training_text = f"""
Service Guide Entry: {service_doc['title']}
Type: {service_doc['type']} | Category: {service_doc['category']}
Sheet: {service_doc['sheet']} | Row: {service_doc['row']}

Description: {service_doc['description']}

Details:
{service_doc['details']}

Keywords: {', '.join(service_doc['keywords'])}

Searchable Content: {service_doc['searchable_content']}
"""
            
            # Add to AI knowledge base
            metadata = {
                "source": "service_guide",
                "type": service_doc['type'],
                "category": service_doc['category'],
                "sheet": service_doc['sheet'],
                "row": service_doc['row'],
                "entry_id": service_doc['id']
            }
            
            success = await self.ai_service.add_document(training_text, metadata)
            return success
            
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {e}")
            return False
    
    async def _save_training_results(self, file_path: str, trained_entries: List[Dict]):
        """Save training results to file"""
        try:
            output_file = f"trained_service_guide_{os.path.basename(file_path).replace('.xlsx', '.json')}"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(trained_entries, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Training results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _create_training_summary(self, trained_entries: List[Dict]) -> Dict:
        """Create training summary statistics"""
        summary = {
            "total_entries": len(trained_entries),
            "types": {},
            "categories": {},
            "sheets": {}
        }
        
        for entry in trained_entries:
            # Count types
            entry_type = entry.get("type", "unknown")
            summary["types"][entry_type] = summary["types"].get(entry_type, 0) + 1
            
            # Count categories
            category = entry.get("category", "unknown")
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            # Count sheets
            sheet = entry.get("sheet", "unknown")
            summary["sheets"][sheet] = summary["sheets"].get(sheet, 0) + 1
        
        return summary

    async def _extract_pdf_service_data(self, file_path: str) -> List[Dict]:
        """Extract service data from PDF file in structured sections"""
        try:
            # Extract raw PDF content
            pdf_content = await self.document_service._extract_from_pdf(file_path)
            
            if not pdf_content:
                return []
            
            # Split PDF content into logical sections
            sections = self._split_pdf_into_sections(pdf_content)
            
            service_entries = []
            
            for section_idx, section in enumerate(sections):
                if len(section.strip()) < 50:  # Skip too short sections
                    continue
                
                # Create structured entry similar to Excel row format
                service_entry = {
                    "section": f"PDF_Section_{section_idx + 1}",
                    "page": section_idx + 1,
                    "data": self._parse_section_content(section),
                    "entry_id": f"pdf_section_{section_idx + 1}",
                    "raw_content": section[:500],  # First 500 chars for reference
                    "content_type": self._detect_content_type(section)
                }
                
                service_entries.append(service_entry)
                
            print(f"📄 Extracted {len(service_entries)} PDF sections for training")
            return service_entries
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return []
    
    def _split_pdf_into_sections(self, content: str) -> List[str]:
        """Split PDF content into logical sections for training with enhanced accuracy"""
        try:
            # Use enhanced section splitting for better accuracy
            enhanced_sections = self.accuracy_enhancer.enhance_section_splitting(content)
            
            # Convert enhanced sections to simple string list while preserving metadata
            sections = []
            self._section_metadata = {}  # Store metadata for later use
            
            for i, section_data in enumerate(enhanced_sections):
                section_content = section_data.get("content", "")
                if len(section_content.strip()) > 50:  # Only meaningful sections
                    sections.append(section_content)
                    # Store metadata for this section
                    self._section_metadata[i] = {
                        "type": section_data.get("type", "general"),
                        "quality_score": section_data.get("quality_score", 0.5),
                        "technical_density": section_data.get("technical_density", 0.0),
                        "structure_quality": section_data.get("structure_quality", 0.0),
                        "has_procedures": section_data.get("has_procedures", False),
                        "has_specifications": section_data.get("has_specifications", False),
                        "has_safety_info": section_data.get("has_safety_info", False),
                        "estimated_importance": section_data.get("estimated_importance", 0.5)
                    }
            
            print(f"📊 Enhanced section analysis: {len(sections)} high-quality sections identified")
            
            return sections
            
        except Exception as e:
            logger.error(f"Enhanced section splitting error: {e}")
            # Fallback to original method
            return self._split_pdf_into_sections_fallback(content)
    
    def _split_pdf_into_sections_fallback(self, content: str) -> List[str]:
        """Fallback section splitting method"""
        try:
            # Split by major headers and section markers
            section_patterns = [
                r'=== [^=]+ ===',  # Enhanced header markers
                r'CHAPTER \d+',
                r'SECTION \d+',
                r'PART \d+',
                r'PROCEDURE_STEP:',
                r'ERROR_CODE_INFO:',
                r'SAFETY_INSTRUCTION:',
                r'MAINTENANCE_TASK:',
                r'TECHNICAL_SPEC:'
            ]
            
            sections = []
            current_section = ""
            
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line starts a new section
                is_section_start = any(
                    re.search(pattern, line, re.IGNORECASE) for pattern in section_patterns
                )
                
                if is_section_start and current_section:
                    # Save current section and start new one
                    if len(current_section.strip()) > 100:  # Only meaningful sections
                        sections.append(current_section.strip())
                    current_section = line + '\n'
                else:
                    current_section += line + '\n'
            
            # Add final section
            if current_section and len(current_section.strip()) > 100:
                sections.append(current_section.strip())
            
            # If no clear sections found, split by length
            if len(sections) < 5:
                sections = self._split_by_length(content)
            
            return sections
            
        except Exception as e:
            logger.error(f"Fallback section splitting error: {e}")
            return [content]  # Return whole content as single section
    
    def _split_by_length(self, content: str, max_length: int = 1000) -> List[str]:
        """Split content by length when no clear section markers found"""
        sections = []
        words = content.split()
        current_section = []
        current_length = 0
        
        for word in words:
            current_section.append(word)
            current_length += len(word) + 1
            
            if current_length >= max_length:
                sections.append(' '.join(current_section))
                current_section = []
                current_length = 0
        
        # Add remaining content
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections
    
    def _parse_section_content(self, section: str) -> Dict:
        """Parse section content into structured data with enhanced accuracy"""
        try:
            # Use enhanced content extraction
            section_data = {"content": section}
            enhanced_data = self.accuracy_enhancer.enhance_content_extraction(section_data)
            
            # Start with basic parsing
            parsed_data = {}
            lines = section.split('\n')
            
            # Extract title/header with enhanced method
            first_line = lines[0].strip() if lines else ""
            if first_line:
                enhanced_title = enhanced_data.get("title")
                parsed_data['title'] = enhanced_title if enhanced_title else first_line
            
            # Add enhanced extracted content
            if enhanced_data.get("procedures"):
                parsed_data['procedures'] = '; '.join(enhanced_data["procedures"][:5])
            
            if enhanced_data.get("specifications"):
                parsed_data['specifications'] = '; '.join(enhanced_data["specifications"][:8])
            
            if enhanced_data.get("safety_info"):
                parsed_data['safety_info'] = '; '.join(enhanced_data["safety_info"][:5])
            
            if enhanced_data.get("maintenance"):
                parsed_data['maintenance'] = '; '.join(enhanced_data["maintenance"][:5])
            
            if enhanced_data.get("technical_parameters"):
                parsed_data['technical_parameters'] = '; '.join(enhanced_data["technical_parameters"][:6])
            
            if enhanced_data.get("error_codes"):
                parsed_data['error_codes'] = '; '.join(enhanced_data["error_codes"][:4])
            
            # Original categorization but enhanced
            content_types = {
                'procedures': [],
                'specifications': [],
                'safety_info': [],
                'maintenance': [],
                'error_codes': [],
                'technical_data': []
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Categorize content with better patterns
                if 'PROCEDURE_STEP:' in line or any(word in line.lower() for word in ['step', 'procedure', 'instruction']):
                    content_types['procedures'].append(line.replace('PROCEDURE_STEP:', '').strip())
                elif 'SPECIFICATION:' in line or ':' in line and any(word in line.lower() for word in ['spec', 'parameter', 'value']):
                    content_types['specifications'].append(line.replace('SPECIFICATION:', '').strip())
                elif 'SAFETY_INSTRUCTION:' in line or any(word in line.lower() for word in ['safety', 'warning', 'caution']):
                    content_types['safety_info'].append(line.replace('SAFETY_INSTRUCTION:', '').strip())
                elif 'MAINTENANCE_TASK:' in line or any(word in line.lower() for word in ['maintenance', 'service', 'lubricate']):
                    content_types['maintenance'].append(line.replace('MAINTENANCE_TASK:', '').strip())
                elif 'ERROR_CODE_INFO:' in line or re.search(r'[E]\d{3,4}|alarm|error', line, re.IGNORECASE):
                    content_types['error_codes'].append(line.replace('ERROR_CODE_INFO:', '').strip())
                elif 'TECHNICAL_SPEC:' in line or any(word in line.lower() for word in ['rpm', 'mm', 'accuracy', 'capacity']):
                    content_types['technical_data'].append(line.replace('TECHNICAL_SPEC:', '').strip())
            
            # Merge original and enhanced categorization
            for category, items in content_types.items():
                if items and category not in parsed_data:
                    parsed_data[category] = '; '.join(items[:5])
            
            # Add content summary if no structured data found
            if len(parsed_data) <= 1:  # Only title found
                parsed_data['content'] = section[:400] + '...' if len(section) > 400 else section
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Enhanced section parsing error: {e}")
            return self._parse_section_content_fallback(section)
    
    def _parse_section_content_fallback(self, section: str) -> Dict:
        """Fallback content parsing method"""
        try:
            parsed_data = {}
            lines = section.split('\n')
            
            # Extract title/header
            first_line = lines[0].strip() if lines else ""
            if first_line:
                parsed_data['title'] = first_line
            
            # Extract key information patterns
            content_types = {
                'procedures': [],
                'specifications': [],
                'safety_info': [],
                'maintenance': [],
                'error_codes': [],
                'technical_data': []
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Categorize content
                if 'PROCEDURE_STEP:' in line:
                    content_types['procedures'].append(line.replace('PROCEDURE_STEP:', '').strip())
                elif 'SPECIFICATION:' in line:
                    content_types['specifications'].append(line.replace('SPECIFICATION:', '').strip())
                elif 'SAFETY_INSTRUCTION:' in line:
                    content_types['safety_info'].append(line.replace('SAFETY_INSTRUCTION:', '').strip())
                elif 'MAINTENANCE_TASK:' in line:
                    content_types['maintenance'].append(line.replace('MAINTENANCE_TASK:', '').strip())
                elif 'ERROR_CODE_INFO:' in line:
                    content_types['error_codes'].append(line.replace('ERROR_CODE_INFO:', '').strip())
                elif 'TECHNICAL_SPEC:' in line:
                    content_types['technical_data'].append(line.replace('TECHNICAL_SPEC:', '').strip())
            
            # Add non-empty categories to parsed data
            for category, items in content_types.items():
                if items:
                    parsed_data[category] = '; '.join(items)
            
            # Add summary if no structured data found
            if len(parsed_data) <= 1:  # Only title found
                parsed_data['content'] = section[:300] + '...' if len(section) > 300 else section
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Fallback section parsing error: {e}")
            return {'content': section[:300]}
    
    def _detect_content_type(self, section: str) -> str:
        """Detect the type of content in this section"""
        section_lower = section.lower()
        
        if any(word in section_lower for word in ['procedure', 'step', 'instruction']):
            return 'procedure'
        elif any(word in section_lower for word in ['safety', 'warning', 'caution']):
            return 'safety'
        elif any(word in section_lower for word in ['maintenance', 'service', 'repair']):
            return 'maintenance'
        elif any(word in section_lower for word in ['error', 'alarm', 'fault']):
            return 'troubleshooting'
        elif any(word in section_lower for word in ['specification', 'technical', 'parameter']):
            return 'technical'
        else:
            return 'general'

    async def _create_pdf_service_documentation(self, entry: Dict) -> Dict:
        """Create structured service documentation for PDF entries"""
        try:
            # Format the raw data for documentation
            data_summary = self._format_pdf_entry_data(entry["data"])
            
            # Determine entry type and category
            entry_type = self._classify_pdf_service_entry(entry)
            
            # Create structured documentation
            service_doc = {
                "id": entry["entry_id"],
                "section": entry["section"],
                "page": entry["page"],
                "type": entry_type["type"],
                "category": entry_type["category"],
                "title": self._generate_pdf_title(entry["data"]),
                "description": self._generate_pdf_description(entry["data"], entry_type),
                "details": data_summary,
                "keywords": self._extract_pdf_keywords(entry["data"]),
                "searchable_content": self._create_pdf_searchable_content(entry["data"]),
                "raw_data": entry["data"],
                "content_type": entry.get("content_type", "general"),
                "source_type": "pdf",
                "confidence_score": self._calculate_pdf_confidence(entry)
            }
            
            return service_doc
            
        except Exception as e:
            logger.error(f"Error creating PDF service documentation: {e}")
            return {
                "id": entry.get("entry_id", "unknown"),
                "error": str(e),
                "raw_data": entry.get("data", {}),
                "source_type": "pdf"
            }
    
    def _format_pdf_entry_data(self, data: Dict) -> str:
        """Format PDF entry data into readable text"""
        formatted_lines = []
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                formatted_lines.append(f"{key.title()}: {value.strip()}")
        return "\n".join(formatted_lines) if formatted_lines else "No structured data available"
    
    def _classify_pdf_service_entry(self, entry: Dict) -> Dict:
        """Classify PDF service entry type and category"""
        content_type = entry.get("content_type", "general")
        data = entry.get("data", {})
        
        # Analyze content for classification
        all_text = " ".join([str(v) for v in data.values() if isinstance(v, str)]).lower()
        
        # Determine type based on content
        if content_type == "procedure":
            entry_type = "procedure"
        elif content_type == "safety":
            entry_type = "safety_instruction"
        elif content_type == "maintenance":
            entry_type = "maintenance_guide"
        elif content_type == "troubleshooting":
            entry_type = "troubleshooting"
        elif content_type == "technical":
            entry_type = "specification"
        else:
            # Analyze text content
            if any(word in all_text for word in ['step', 'procedure', 'instruction', 'operation']):
                entry_type = "procedure"
            elif any(word in all_text for word in ['safety', 'warning', 'caution', 'danger']):
                entry_type = "safety_instruction"
            elif any(word in all_text for word in ['maintenance', 'service', 'repair', 'lubricate']):
                entry_type = "maintenance_guide"
            elif any(word in all_text for word in ['error', 'alarm', 'fault', 'troubleshoot']):
                entry_type = "troubleshooting"
            elif any(word in all_text for word in ['specification', 'parameter', 'technical', 'accuracy']):
                entry_type = "specification"
            else:
                entry_type = "general_information"
        
        # Determine category
        if any(word in all_text for word in ['cnc', 'machine', 'pmc']):
            category = "cnc_machine"
        elif any(word in all_text for word in ['spindle', 'axis', 'motor']):
            category = "machine_components"
        elif any(word in all_text for word in ['programming', 'code', 'g-code']):
            category = "programming"
        elif any(word in all_text for word in ['maintenance', 'service']):
            category = "maintenance"
        elif any(word in all_text for word in ['safety', 'protective']):
            category = "safety"
        else:
            category = "general"
        
        return {
            "type": entry_type,
            "category": category
        }
    
    def _generate_pdf_title(self, data: Dict) -> str:
        """Generate title for PDF entry"""
        if "title" in data and data["title"]:
            return data["title"][:100]  # Limit title length
        
        # Try to extract title from other fields
        for key, value in data.items():
            if isinstance(value, str) and len(value.strip()) > 10 and len(value.strip()) < 150:
                return value.strip()[:100]
        
        return "PDF Content Section"
    
    def _generate_pdf_description(self, data: Dict, entry_type: Dict) -> str:
        """Generate description for PDF entry"""
        desc_parts = []
        
        # Add type-based description
        desc_parts.append(f"This is a {entry_type['type'].replace('_', ' ')} from the PDF manual.")
        
        # Add content summary
        content_items = []
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                if key != "title":  # Don't repeat title
                    content_items.append(f"{key}: {value[:100]}...")
        
        if content_items:
            desc_parts.append("Content includes: " + "; ".join(content_items[:3]))
        
        return " ".join(desc_parts)
    
    def _extract_pdf_keywords(self, data: Dict) -> List[str]:
        """Extract keywords from PDF entry data"""
        keywords = set()
        
        for key, value in data.items():
            if isinstance(value, str):
                # Extract important words
                words = value.lower().split()
                for word in words:
                    word = word.strip('.,!?():;[]{}')
                    if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been']:
                        keywords.add(word)
        
        # Add technical keywords
        all_text = " ".join([str(v) for v in data.values() if isinstance(v, str)]).lower()
        tech_keywords = ['cnc', 'pmc', 'spindle', 'axis', 'safety', 'maintenance', 'procedure', 'specification']
        for keyword in tech_keywords:
            if keyword in all_text:
                keywords.add(keyword)
        
        return list(keywords)[:20]  # Limit to 20 keywords
    
    def _create_pdf_searchable_content(self, data: Dict) -> str:
        """Create searchable content from PDF entry"""
        content_parts = []
        
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                content_parts.append(f"{key}: {value}")
        
        return " | ".join(content_parts)
    
    def _calculate_pdf_confidence(self, entry: Dict) -> float:
        """Calculate enhanced confidence score for PDF entry"""
        try:
            # Get section metadata if available
            section_idx = int(entry.get("entry_id", "").split("_")[-1]) - 1
            section_metadata = getattr(self, '_section_metadata', {}).get(section_idx, {})
            
            # If we have enhanced metadata, use it for better confidence calculation
            if section_metadata:
                section_data = {
                    "quality_score": section_metadata.get("quality_score", 0.5),
                    "technical_density": section_metadata.get("technical_density", 0.0),
                    "structure_quality": section_metadata.get("structure_quality", 0.0)
                }
                
                extracted_data = entry.get("data", {})
                enhanced_confidence = self.accuracy_enhancer.calculate_enhanced_confidence(section_data, extracted_data)
                return enhanced_confidence
            
            # Fallback to original confidence calculation
            confidence = 0.5  # Base confidence
            
            data = entry.get("data", {})
            
            # Increase confidence based on structured content
            if len(data) > 3:
                confidence += 0.2
            
            # Increase confidence based on content quality
            total_length = sum(len(str(v)) for v in data.values() if isinstance(v, str))
            if total_length > 100:
                confidence += 0.1
            if total_length > 300:
                confidence += 0.1
            
            # Increase confidence based on content type
            content_type = entry.get("content_type", "general")
            if content_type != "general":
                confidence += 0.1
            
            # Bonus for rich content types
            content_richness = 0
            rich_fields = ['procedures', 'specifications', 'safety_info', 'maintenance', 'technical_parameters']
            for field in rich_fields:
                if field in data and data[field]:
                    content_richness += 1
            
            confidence += (content_richness / len(rich_fields)) * 0.2
            
            return min(confidence, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Enhanced confidence calculation error: {e}")
            return 0.6  # Default moderate confidence
    
    async def _add_pdf_to_ai_knowledge_base(self, service_doc: Dict) -> Dict:
        """Add PDF service document to AI knowledge base"""
        try:
            # Create content for AI knowledge base
            content_parts = [
                f"Title: {service_doc.get('title', 'N/A')}",
                f"Type: {service_doc.get('type', 'N/A')}",
                f"Category: {service_doc.get('category', 'N/A')}",
                f"Section: {service_doc.get('section', 'N/A')}",
                f"Description: {service_doc.get('description', 'N/A')}",
                f"Details: {service_doc.get('details', 'N/A')}",
                f"Keywords: {', '.join(service_doc.get('keywords', []))}",
                f"Searchable Content: {service_doc.get('searchable_content', 'N/A')}"
            ]
            
            structured_content = "\n".join(content_parts)
            
            # Add to AI service knowledge base
            knowledge_entry = {
                "content": structured_content,
                "metadata": {
                    "source": "pdf_service_guide",
                    "type": service_doc.get("type", "unknown"),
                    "category": service_doc.get("category", "unknown"),
                    "section": service_doc.get("section", "unknown"),
                    "confidence": service_doc.get("confidence_score", 0.5)
                }
            }
            
            # Store in AI knowledge base
            await self.ai_service.add_document(structured_content, knowledge_entry["metadata"])
            
            return knowledge_entry
            
        except Exception as e:
            logger.error(f"Error adding PDF to knowledge base: {e}")
            return {"error": str(e)}

async def main():
    """Test the enhanced service guide trainer"""
    trainer = EnhancedServiceGuideTrainer()
    
    # Test with CNC data
    result = await trainer.train_excel_service_guide("test_cnc_data.xlsx")
    
    if result["success"]:
        print(f"\n🎉 Training Summary:")
        print(f"📊 Total entries: {result['entries_trained']}")
        print(f"🧠 Knowledge base entries: {result['knowledge_base_entries']}")
        
        summary = result["training_summary"]
        print(f"\n📋 By Type: {summary['types']}")
        print(f"📂 By Category: {summary['categories']}")
        print(f"📄 By Sheet: {summary['sheets']}")
        
        # Show sample entry
        if result["sample_entries"]:
            sample = result["sample_entries"][0]
            print(f"\n📋 Sample Entry:")
            print(f"   Title: {sample['title']}")
            print(f"   Type: {sample['type']} | Category: {sample['category']}")
            print(f"   Keywords: {', '.join(sample['keywords'][:5])}...")
    else:
        print(f"❌ Training failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
