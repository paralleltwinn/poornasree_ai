#!/usr/bin/env python3
"""
PDF Training Accuracy Enhancement Module
Implements advanced techniques to improve PDF training accuracy to match Excel quality
"""

import re
import logging
from typing import Dict, List, Tuple
import nltk
from collections import Counter

logger = logging.getLogger(__name__)

class PDFAccuracyEnhancer:
    """Advanced PDF processing for higher training accuracy"""
    
    def __init__(self):
        self.technical_terms = {
            'cnc_terms': ['cnc', 'pmc', 'fanuc', 'siemens', 'haas', 'mazak', 'okuma'],
            'machine_parts': ['spindle', 'axis', 'motor', 'servo', 'encoder', 'bearing', 'chuck'],
            'operations': ['machining', 'cutting', 'drilling', 'milling', 'turning', 'boring'],
            'safety_terms': ['safety', 'warning', 'caution', 'danger', 'protective', 'emergency'],
            'maintenance_terms': ['maintenance', 'lubrication', 'inspection', 'calibration', 'replacement'],
            'programming_terms': ['g-code', 'programming', 'parameter', 'offset', 'coordinate'],
            'error_terms': ['alarm', 'error', 'fault', 'troubleshooting', 'diagnostic']
        }
        
        self.quality_patterns = {
            'procedure_patterns': [
                r'step\s+\d+',
                r'\d+\.\s+[A-Z]',
                r'procedure\s+for',
                r'instructions?\s+for',
                r'how\s+to'
            ],
            'specification_patterns': [
                r'\d+\s*mm',
                r'\d+\s*rpm',
                r'\d+\s*kg',
                r'accuracy:\s*[\d\.]+',
                r'tolerance:\s*[\d\.]+',
                r'capacity:\s*[\d\.]+',
                r'max\s*:\s*[\d\.]+'
            ],
            'safety_patterns': [
                r'warning[:\s]',
                r'caution[:\s]',
                r'danger[:\s]',
                r'do\s+not',
                r'must\s+wear',
                r'protective\s+equipment'
            ],
            'maintenance_patterns': [
                r'every\s+\d+\s+hours?',
                r'daily\s+check',
                r'weekly\s+maintenance',
                r'monthly\s+inspection',
                r'replace\s+when',
                r'lubricate\s+every'
            ]
        }
    
    def enhance_section_splitting(self, content: str) -> List[Dict]:
        """Enhanced section splitting with better accuracy"""
        sections = []
        
        # First, identify major structural elements
        structural_markers = [
            r'(?i)chapter\s+\d+',
            r'(?i)section\s+\d+',
            r'(?i)part\s+\d+',
            r'(?i)appendix\s+[a-z]',
            r'(?i)table\s+of\s+contents',
            r'(?i)index',
            r'(?i)specifications?',
            r'(?i)maintenance\s+schedule',
            r'(?i)troubleshooting\s+guide',
            r'(?i)safety\s+instructions?',
            r'(?i)operating\s+procedures?'
        ]
        
        # Split by structural markers
        current_section = ""
        current_metadata = {"type": "general", "confidence": 0.5}
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for structural markers
            marker_found = False
            for pattern in structural_markers:
                if re.search(pattern, line):
                    # Save previous section
                    if current_section and len(current_section.strip()) > 100:
                        section_data = self._analyze_section_content(current_section)
                        sections.append({
                            "content": current_section.strip(),
                            "line_start": max(0, line_num - len(current_section.split('\n'))),
                            "line_end": line_num,
                            **section_data
                        })
                    
                    # Start new section
                    current_section = line + '\n'
                    current_metadata = self._classify_by_marker(line)
                    marker_found = True
                    break
            
            if not marker_found:
                current_section += line + '\n'
        
        # Add final section
        if current_section and len(current_section.strip()) > 100:
            section_data = self._analyze_section_content(current_section)
            sections.append({
                "content": current_section.strip(),
                "line_start": max(0, len(lines) - len(current_section.split('\n'))),
                "line_end": len(lines),
                **section_data
            })
        
        # If no structural sections found, use intelligent content-based splitting
        if len(sections) < 3:
            sections = self._intelligent_content_splitting(content)
        
        return sections
    
    def _analyze_section_content(self, content: str) -> Dict:
        """Analyze section content for type, quality, and metadata"""
        analysis = {
            "type": "general",
            "quality_score": 0.5,
            "technical_density": 0.0,
            "structure_quality": 0.0,
            "key_terms": [],
            "has_procedures": False,
            "has_specifications": False,
            "has_safety_info": False,
            "estimated_importance": 0.5
        }
        
        content_lower = content.lower()
        
        # Analyze technical density
        technical_count = 0
        total_terms = 0
        
        for category, terms in self.technical_terms.items():
            for term in terms:
                count = content_lower.count(term)
                if count > 0:
                    technical_count += count
                    analysis["key_terms"].append(term)
                    total_terms += 1
        
        # Calculate technical density
        words = content.split()
        if len(words) > 0:
            analysis["technical_density"] = technical_count / len(words)
        
        # Analyze structure quality
        structure_indicators = 0
        
        # Check for numbered lists
        if re.search(r'\d+\.\s+[A-Z]', content):
            structure_indicators += 1
            analysis["has_procedures"] = True
        
        # Check for bullet points
        if re.search(r'[•\-\*]\s+', content):
            structure_indicators += 1
        
        # Check for tables or specifications
        if re.search(r':\s*[\d\.]+', content):
            structure_indicators += 1
            analysis["has_specifications"] = True
        
        # Check for safety information
        for pattern in self.quality_patterns['safety_patterns']:
            if re.search(pattern, content, re.IGNORECASE):
                analysis["has_safety_info"] = True
                structure_indicators += 1
                break
        
        analysis["structure_quality"] = min(structure_indicators / 4.0, 1.0)
        
        # Determine content type
        type_scores = {}
        
        # Score each type based on pattern matching
        for type_name, patterns in self.quality_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches
            type_scores[type_name.replace('_patterns', '')] = score
        
        # Select best type
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                analysis["type"] = best_type
        
        # Calculate overall quality score
        quality_factors = [
            analysis["technical_density"] * 2,  # Technical content is important
            analysis["structure_quality"],      # Good structure is important
            min(len(analysis["key_terms"]) / 10.0, 1.0),  # Keyword diversity
            min(len(content) / 1000.0, 1.0)    # Content length (up to optimal)
        ]
        
        analysis["quality_score"] = sum(quality_factors) / len(quality_factors)
        analysis["estimated_importance"] = min(analysis["quality_score"] * 1.5, 1.0)
        
        return analysis
    
    def _classify_by_marker(self, marker_line: str) -> Dict:
        """Classify section type based on structural marker"""
        marker_lower = marker_line.lower()
        
        if any(word in marker_lower for word in ['safety', 'warning', 'caution']):
            return {"type": "safety", "confidence": 0.9}
        elif any(word in marker_lower for word in ['maintenance', 'service']):
            return {"type": "maintenance", "confidence": 0.9}
        elif any(word in marker_lower for word in ['specification', 'technical', 'parameter']):
            return {"type": "specification", "confidence": 0.9}
        elif any(word in marker_lower for word in ['procedure', 'operation', 'instruction']):
            return {"type": "procedure", "confidence": 0.9}
        elif any(word in marker_lower for word in ['troubleshooting', 'problem', 'error', 'alarm']):
            return {"type": "troubleshooting", "confidence": 0.9}
        else:
            return {"type": "general", "confidence": 0.6}
    
    def _intelligent_content_splitting(self, content: str) -> List[Dict]:
        """Split content intelligently when no clear structure markers exist"""
        sections = []
        
        # Split by paragraph breaks and content changes
        paragraphs = re.split(r'\n\s*\n', content)
        
        current_section = ""
        current_type = "general"
        
        for para in paragraphs:
            if len(para.strip()) < 20:  # Skip very short paragraphs
                continue
            
            # Analyze paragraph type
            para_analysis = self._analyze_section_content(para)
            para_type = para_analysis["type"]
            
            # If type changes significantly or section gets too long, start new section
            if (para_type != current_type and current_section) or len(current_section) > 1500:
                if current_section:
                    section_data = self._analyze_section_content(current_section)
                    sections.append({
                        "content": current_section.strip(),
                        **section_data
                    })
                
                current_section = para + '\n\n'
                current_type = para_type
            else:
                current_section += para + '\n\n'
        
        # Add final section
        if current_section:
            section_data = self._analyze_section_content(current_section)
            sections.append({
                "content": current_section.strip(),
                **section_data
            })
        
        return sections
    
    def enhance_content_extraction(self, section_data: Dict) -> Dict:
        """Extract structured content with higher accuracy"""
        content = section_data.get("content", "")
        enhanced_data = {}
        
        # Extract title with better accuracy
        title = self._extract_enhanced_title(content)
        if title:
            enhanced_data["title"] = title
        
        # Extract procedures with numbering
        procedures = self._extract_procedures(content)
        if procedures:
            enhanced_data["procedures"] = procedures
        
        # Extract specifications with values
        specifications = self._extract_specifications(content)
        if specifications:
            enhanced_data["specifications"] = specifications
        
        # Extract safety information
        safety_info = self._extract_safety_information(content)
        if safety_info:
            enhanced_data["safety_info"] = safety_info
        
        # Extract maintenance instructions
        maintenance = self._extract_maintenance_instructions(content)
        if maintenance:
            enhanced_data["maintenance"] = maintenance
        
        # Extract technical parameters
        parameters = self._extract_technical_parameters(content)
        if parameters:
            enhanced_data["technical_parameters"] = parameters
        
        # Extract error codes and meanings
        error_codes = self._extract_error_codes(content)
        if error_codes:
            enhanced_data["error_codes"] = error_codes
        
        return enhanced_data
    
    def _extract_enhanced_title(self, content: str) -> str:
        """Extract title with better accuracy"""
        lines = content.split('\n')
        
        # Look for enhanced header markers
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line:
                continue
            
            # Check for header patterns
            if re.match(r'===.*===', line):
                return re.sub(r'[=]+', '', line).strip()
            elif re.match(r'CHAPTER\s+\d+', line, re.IGNORECASE):
                return line
            elif re.match(r'SECTION\s+\d+', line, re.IGNORECASE):
                return line
            elif line.isupper() and len(line) > 10 and len(line) < 80:
                return line
            elif re.match(r'\d+\.\s+[A-Z]', line) and len(line) < 80:
                return line
        
        # Fallback to first meaningful line
        for line in lines[:3]:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                return line
        
        return "PDF Section"
    
    def _extract_procedures(self, content: str) -> List[str]:
        """Extract step-by-step procedures"""
        procedures = []
        
        # Find numbered steps
        step_pattern = r'(\d+[\.\)]\s+.*?)(?=\d+[\.\)]|\n\n|$)'
        matches = re.findall(step_pattern, content, re.DOTALL)
        
        for match in matches:
            step = match.strip()
            if len(step) > 10:  # Meaningful steps only
                procedures.append(step)
        
        return procedures[:10]  # Limit to 10 procedures
    
    def _extract_specifications(self, content: str) -> List[str]:
        """Extract technical specifications"""
        specs = []
        
        # Pattern for specifications with values
        spec_patterns = [
            r'([A-Za-z][^:]*?):\s*([\d\.]+\s*[a-zA-Z]*)',
            r'(Max\w*|Min\w*|Accuracy|Tolerance|Capacity)\s*:?\s*([\d\.]+\s*[a-zA-Z]*)',
            r'([A-Z][^:]{5,30}):\s*([\d\.]+(?:\s*[a-zA-Z/]+)*)'
        ]
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for name, value in matches:
                spec = f"{name.strip()}: {value.strip()}"
                if spec not in specs and len(spec) > 5:
                    specs.append(spec)
        
        return specs[:15]  # Limit to 15 specifications
    
    def _extract_safety_information(self, content: str) -> List[str]:
        """Extract safety-related information"""
        safety_items = []
        
        # Look for safety-related sentences
        sentences = re.split(r'[.!?]+', content)
        
        safety_keywords = ['warning', 'caution', 'danger', 'safety', 'protective', 'emergency', 'hazard']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in safety_keywords) and len(sentence) > 20:
                safety_items.append(sentence)
        
        return safety_items[:8]  # Limit to 8 safety items
    
    def _extract_maintenance_instructions(self, content: str) -> List[str]:
        """Extract maintenance instructions"""
        maintenance_items = []
        
        # Look for maintenance-related content
        maintenance_patterns = [
            r'(lubricate.*?(?=\.|$))',
            r'(inspect.*?(?=\.|$))',
            r'(replace.*?(?=\.|$))',
            r'(clean.*?(?=\.|$))',
            r'(check.*?(?=\.|$))',
            r'(calibrate.*?(?=\.|$))'
        ]
        
        for pattern in maintenance_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                item = match.strip()
                if len(item) > 15 and item not in maintenance_items:
                    maintenance_items.append(item)
        
        return maintenance_items[:10]  # Limit to 10 maintenance items
    
    def _extract_technical_parameters(self, content: str) -> List[str]:
        """Extract technical parameters and their values"""
        parameters = []
        
        # Look for parameter patterns
        param_patterns = [
            r'(Speed|RPM|Feed|Torque|Power|Voltage|Current|Temperature|Pressure)\s*:?\s*([\d\.]+\s*[a-zA-Z/%]*)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*:?\s*([\d\.]+\s*[a-zA-Z/%]*)'
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for param, value in matches:
                parameter = f"{param.strip()}: {value.strip()}"
                if parameter not in parameters:
                    parameters.append(parameter)
        
        return parameters[:12]  # Limit to 12 parameters
    
    def _extract_error_codes(self, content: str) -> List[str]:
        """Extract error codes and their descriptions"""
        error_codes = []
        
        # Look for error code patterns
        error_patterns = [
            r'([E]\d{3,4})\s*:?\s*([^.]*)',
            r'(Alarm\s+\d+)\s*:?\s*([^.]*)',
            r'(Error\s+\d+)\s*:?\s*([^.]*)'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for code, description in matches:
                error_info = f"{code.strip()}: {description.strip()}"
                if len(error_info) > 10 and error_info not in error_codes:
                    error_codes.append(error_info)
        
        return error_codes[:8]  # Limit to 8 error codes
    
    def calculate_enhanced_confidence(self, section_data: Dict, extracted_data: Dict) -> float:
        """Calculate enhanced confidence score"""
        base_confidence = 0.4  # Start with base confidence
        
        # Quality factors
        quality_score = section_data.get("quality_score", 0.5)
        base_confidence += quality_score * 0.3
        
        # Content richness
        content_factors = len(extracted_data)
        if content_factors > 5:
            base_confidence += 0.2
        elif content_factors > 3:
            base_confidence += 0.1
        
        # Technical density
        technical_density = section_data.get("technical_density", 0.0)
        base_confidence += technical_density * 0.2
        
        # Structure quality
        structure_quality = section_data.get("structure_quality", 0.0)
        base_confidence += structure_quality * 0.15
        
        # Specific content bonuses
        if extracted_data.get("procedures"):
            base_confidence += 0.1
        if extracted_data.get("specifications"):
            base_confidence += 0.1
        if extracted_data.get("safety_info"):
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)  # Cap at 1.0
