#!/usr/bin/env python3
"""
Create an enhanced test PDF with better structured content for improved AI recognition
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def create_enhanced_test_pdf():
    """Create an enhanced test PDF with clearly structured content"""
    filename = "enhanced_cnc_manual.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=inch, bottomMargin=inch)
    
    # Get sample styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                fontSize=16, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], 
                                  fontSize=14, spaceAfter=12, textColor=colors.blue)
    
    story = []
    
    # Title Page
    story.append(Paragraph("PMC-2000 CNC MACHINE MANUAL", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Model: PMC-2000", styles['Normal']))
    story.append(Paragraph("Serial Number: PMC2000-001", styles['Normal']))
    story.append(Paragraph("Manufacturing Date: 2024", styles['Normal']))
    story.append(Spacer(1, 40))
    
    # Chapter 1: Safety Instructions
    story.append(Paragraph("CHAPTER 1: SAFETY INSTRUCTIONS", heading_style))
    story.append(Paragraph("SAFETY CRITICAL REQUIREMENTS:", styles['Heading3']))
    story.append(Paragraph("• Always wear safety glasses and hearing protection", styles['Normal']))
    story.append(Paragraph("• Steel-toed safety boots required", styles['Normal']))
    story.append(Paragraph("• Close-fitting clothing (no loose sleeves)", styles['Normal']))
    story.append(Paragraph("• Emergency stop button must be functional", styles['Normal']))
    story.append(Paragraph("• Never operate without proper training", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Chapter 2: Machine Specifications
    story.append(Paragraph("CHAPTER 2: MACHINE SPECIFICATIONS", heading_style))
    story.append(Paragraph("PMC-2000 TECHNICAL SPECIFICATIONS:", styles['Heading3']))
    
    # Specifications table
    spec_data = [
        ['Parameter', 'Value', 'Unit', 'Notes'],
        ['Maximum Spindle Speed', '12000', 'RPM', 'Variable frequency control'],
        ['Spindle Motor Power', '15', 'kW', '20 HP equivalent'],
        ['X-Axis Travel', '1200', 'mm', '47.2 inches'],
        ['Y-Axis Travel', '800', 'mm', '31.5 inches'],
        ['Z-Axis Travel', '600', 'mm', '23.6 inches'],
        ['Positioning Accuracy', '±0.005', 'mm', 'Tested per ISO 230'],
        ['Tool Magazine Capacity', '24', 'tools', 'Automatic tool changer'],
        ['Weight', '3500', 'kg', '7716 lbs'],
    ]
    
    spec_table = Table(spec_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1.5*inch])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 20))
    
    # Chapter 3: Operating Procedures
    story.append(Paragraph("CHAPTER 3: OPERATING PROCEDURES", heading_style))
    story.append(Paragraph("MACHINE STARTUP SEQUENCE:", styles['Heading3']))
    story.append(Paragraph("1. Perform pre-startup inspection checklist", styles['Normal']))
    story.append(Paragraph("2. Turn main power switch ON", styles['Normal']))
    story.append(Paragraph("3. Wait for system initialization (approximately 45 seconds)", styles['Normal']))
    story.append(Paragraph("4. Verify all axis position indicators show HOME position", styles['Normal']))
    story.append(Paragraph("5. Load required CNC program", styles['Normal']))
    story.append(Paragraph("6. Install appropriate tooling in magazine", styles['Normal']))
    story.append(Paragraph("7. Set workpiece coordinates and zero points", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Chapter 4: Maintenance Procedures
    story.append(Paragraph("CHAPTER 4: MAINTENANCE PROCEDURES", heading_style))
    story.append(Paragraph("SCHEDULED MAINTENANCE:", styles['Heading3']))
    
    maintenance_data = [
        ['Task', 'Frequency', 'Duration', 'Notes'],
        ['Lubricate ball screws', 'Every 40 hours', '15 minutes', 'Use specified grease only'],
        ['Check coolant level', 'Daily', '5 minutes', 'Top up as needed'],
        ['Clean chip conveyor', 'Weekly', '30 minutes', 'Remove all metal chips'],
        ['Inspect tool magazine', 'Monthly', '45 minutes', 'Check tool retention'],
        ['Calibrate positioning', 'Quarterly', '2 hours', 'Use laser interferometer'],
    ]
    
    maint_table = Table(maintenance_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.8*inch])
    maint_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(maint_table)
    story.append(Spacer(1, 20))
    
    # Chapter 5: Troubleshooting Guide
    story.append(Paragraph("CHAPTER 5: TROUBLESHOOTING GUIDE", heading_style))
    story.append(Paragraph("ERROR CODES AND SOLUTIONS:", styles['Heading3']))
    story.append(Paragraph("ERROR E100: Spindle Overheat", styles['Heading4']))
    story.append(Paragraph("Cause: Excessive spindle RPM or insufficient coolant", styles['Normal']))
    story.append(Paragraph("Solution: Reduce RPM, check coolant flow, verify temperature sensors", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("ERROR E200: Axis Following Error", styles['Heading4']))
    story.append(Paragraph("Cause: Mechanical binding or servo drive malfunction", styles['Normal']))
    story.append(Paragraph("Solution: Check axis movement, inspect ball screws, verify servo parameters", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("ERROR E300: Tool Change Timeout", styles['Heading4']))
    story.append(Paragraph("Cause: Tool magazine mechanical issue or sensor fault", styles['Normal']))
    story.append(Paragraph("Solution: Inspect tool magazine rotation, check sensors, verify tool presence", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Chapter 6: Technical Support
    story.append(Paragraph("CHAPTER 6: TECHNICAL SUPPORT", heading_style))
    story.append(Paragraph("WARRANTY INFORMATION:", styles['Heading3']))
    story.append(Paragraph("• Machine warranty: 3 years from delivery date", styles['Normal']))
    story.append(Paragraph("• Spindle warranty: 2 years or 8000 operating hours", styles['Normal']))
    story.append(Paragraph("• Software support: 5 years with annual updates", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("TRAINING COURSES:", styles['Heading3']))
    story.append(Paragraph("• Basic Operation Certification (40 hours)", styles['Normal']))
    story.append(Paragraph("• Advanced Programming (80 hours)", styles['Normal']))
    story.append(Paragraph("• Maintenance Technician Course (120 hours)", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("CONTACT INFORMATION:", styles['Heading3']))
    story.append(Paragraph("Technical Support: +1-800-CNC-HELP", styles['Normal']))
    story.append(Paragraph("Emergency Service: +1-800-CNC-911", styles['Normal']))
    story.append(Paragraph("Email: support@pmc-cnc.com", styles['Normal']))
    
    # Build the PDF
    doc.build(story)
    
    import os
    file_size = os.path.getsize(filename)
    print(f"✅ Enhanced PDF created: {filename}")
    print(f"📄 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    print(f"📋 Features: Enhanced structured content, clear chapter divisions, detailed specifications")
    
    return filename

if __name__ == "__main__":
    create_enhanced_test_pdf()
