#!/usr/bin/env python3
"""
Create a test PDF file with multiple sections for testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def create_test_pdf():
    """Create a test PDF file with comprehensive CNC machine manual content"""
    print("🔧 Creating test PDF file with multiple sections...")
    
    filename = "test_cnc_manual.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkred
    )
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.red,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=12
    )
    
    # Build content
    story = []
    
    # Title Page
    story.append(Paragraph("CNC PRECISION MACHINING CENTER", title_style))
    story.append(Paragraph("Model: PMC-2000 Advanced", styles['Heading2']))
    story.append(Paragraph("Complete Operation and Maintenance Manual", styles['Heading3']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Document Version: 2.1", styles['Normal']))
    story.append(Paragraph("Release Date: July 2025", styles['Normal']))
    story.append(Paragraph("Manual Code: PMC-2000-MAN-2025", styles['Normal']))
    story.append(Spacer(1, 40))
    
    # Safety Section
    story.append(Paragraph("CHAPTER 1: SAFETY INSTRUCTIONS", heading_style))
    story.append(Paragraph("⚠️ WARNING: Read all safety instructions before operating this machine.", warning_style))
    
    safety_content = """
    <b>Critical Safety Requirements:</b><br/>
    • Always wear safety glasses and hearing protection<br/>
    • Ensure emergency stop button is functional before operation<br/>
    • Never leave machine unattended during operation<br/>
    • Maintain minimum 3-foot clearance around machine<br/>
    • Check all guards and safety interlocks before startup<br/>
    • Only trained operators should use this equipment<br/>
    <br/>
    <b>Personal Protective Equipment (PPE):</b><br/>
    • Safety glasses with side shields (ANSI Z87.1)<br/>
    • Steel-toed safety boots<br/>
    • Close-fitting clothing (no loose sleeves)<br/>
    • Hair restraints for long hair<br/>
    • No jewelry or loose items near moving parts
    """
    story.append(Paragraph(safety_content, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Machine Specifications
    story.append(Paragraph("CHAPTER 2: MACHINE SPECIFICATIONS", heading_style))
    
    spec_data = [
        ['Specification', 'Value', 'Unit', 'Notes'],
        ['Maximum Spindle Speed', '12000', 'RPM', 'Variable frequency control'],
        ['Spindle Motor Power', '15', 'kW', '3-phase, 380V'],
        ['Table Dimensions', '1500 x 1000', 'mm', 'T-slot configuration'],
        ['Maximum Load Capacity', '2000', 'kg', 'Evenly distributed'],
        ['X-Axis Travel', '1200', 'mm', 'Ball screw driven'],
        ['Y-Axis Travel', '800', 'mm', 'Ball screw driven'],
        ['Z-Axis Travel', '600', 'mm', 'Ball screw driven'],
        ['Positioning Accuracy', '±0.005', 'mm', 'Tested per ISO 230'],
        ['Repeatability', '±0.003', 'mm', 'Statistical measurement'],
        ['Tool Magazine Capacity', '24', 'tools', 'Automatic tool changer']
    ]
    
    spec_table = Table(spec_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 2*inch])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 20))
    
    # Operating Procedures
    story.append(Paragraph("CHAPTER 3: OPERATING PROCEDURES", heading_style))
    
    startup_content = """
    <b>3.1 Machine Startup Sequence:</b><br/>
    <br/>
    <b>Step 1: Pre-startup Inspection</b><br/>
    • Verify machine area is clear of personnel and obstacles<br/>
    • Check coolant level (minimum 80% capacity)<br/>
    • Inspect all guards and safety devices<br/>
    • Ensure emergency stop circuits are functional<br/>
    <br/>
    <b>Step 2: Power-On Sequence</b><br/>
    • Turn main electrical disconnect to ON position<br/>
    • Press control panel POWER button<br/>
    • Wait for system initialization (approximately 45 seconds)<br/>
    • Verify all axis position indicators show "HOME REQUIRED"<br/>
    <br/>
    <b>Step 3: System Initialization</b><br/>
    • Press HOME ALL AXES button on control panel<br/>
    • Machine will automatically home X, Y, and Z axes<br/>
    • Spindle will perform automatic orientation<br/>
    • Tool magazine will cycle to position 1<br/>
    • Wait for "READY" status on main display<br/>
    <br/>
    <b>Step 4: Tool Preparation</b><br/>
    • Load required tools into magazine positions<br/>
    • Update tool length offsets in controller<br/>
    • Perform tool measurement cycle if required<br/>
    • Verify tool data in offset table
    """
    story.append(Paragraph(startup_content, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Maintenance Schedule
    story.append(Paragraph("CHAPTER 4: MAINTENANCE PROCEDURES", heading_style))
    
    maintenance_data = [
        ['Maintenance Task', 'Frequency', 'Estimated Time', 'Skill Level'],
        ['Lubricate ball screws', 'Daily', '15 minutes', 'Operator'],
        ['Check coolant concentration', 'Daily', '10 minutes', 'Operator'],
        ['Clean chip conveyor', 'Daily', '20 minutes', 'Operator'],
        ['Inspect tool holders', 'Weekly', '30 minutes', 'Technician'],
        ['Calibrate probe system', 'Monthly', '2 hours', 'Technician'],
        ['Replace spindle bearings', 'Annually', '8 hours', 'Specialist'],
        ['Update control software', 'As needed', '4 hours', 'Engineer'],
        ['Geometric accuracy check', 'Semi-annually', '6 hours', 'Specialist']
    ]
    
    maintenance_table = Table(maintenance_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch, 1.2*inch])
    maintenance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(maintenance_table)
    story.append(Spacer(1, 20))
    
    # Troubleshooting
    story.append(Paragraph("CHAPTER 5: TROUBLESHOOTING GUIDE", heading_style))
    
    troubleshooting_content = """
    <b>5.1 Common Error Codes and Solutions:</b><br/>
    <br/>
    <b>Error E100 - Spindle Overheat:</b><br/>
    • Cause: Excessive cutting speed or inadequate cooling<br/>
    • Solution: Reduce spindle RPM, check coolant flow and concentration<br/>
    • Prevention: Monitor cutting parameters, maintain coolant system<br/>
    <br/>
    <b>Error E200 - Axis Following Error:</b><br/>
    • Cause: Mechanical obstruction or drive system malfunction<br/>
    • Solution: Clear obstruction, check ball screw lubrication<br/>
    • Prevention: Regular lubrication, avoid overloading axes<br/>
    <br/>
    <b>Error E300 - Tool Break Detection:</b><br/>
    • Cause: Tool breakage during machining operation<br/>
    • Solution: Replace broken tool, verify cutting parameters<br/>
    • Prevention: Use appropriate speeds/feeds, tool condition monitoring<br/>
    <br/>
    <b>Error E400 - Emergency Stop Activated:</b><br/>
    • Cause: Safety circuit interruption or operator intervention<br/>
    • Solution: Clear safety condition, reset emergency stop<br/>
    • Prevention: Maintain safety systems, proper operator training<br/>
    <br/>
    <b>5.2 Performance Optimization:</b><br/>
    • Monitor vibration levels during operation<br/>
    • Maintain optimal cutting fluid temperature (68-72°F)<br/>
    • Keep work area clean and organized<br/>
    • Perform regular geometric accuracy checks<br/>
    • Update control software as recommended by manufacturer
    """
    story.append(Paragraph(troubleshooting_content, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Technical Support
    story.append(Paragraph("CHAPTER 6: TECHNICAL SUPPORT", heading_style))
    
    support_content = """
    <b>Contact Information:</b><br/>
    • Technical Support Hotline: 1-800-CNC-HELP<br/>
    • Email Support: support@precision-cnc.com<br/>
    • Service Portal: www.precision-cnc.com/service<br/>
    • Emergency Service: Available 24/7 for critical issues<br/>
    <br/>
    <b>Warranty Information:</b><br/>
    • Machine warranty: 3 years parts and labor<br/>
    • Control system warranty: 2 years parts and labor<br/>
    • Spindle warranty: 5 years or 10,000 operating hours<br/>
    • Extended warranty options available<br/>
    <br/>
    <b>Training Resources:</b><br/>
    • Operator certification course: 40 hours<br/>
    • Maintenance technician course: 80 hours<br/>
    • Programming workshop: 24 hours<br/>
    • Online training portal with video tutorials<br/>
    <br/>
    End of Manual - Document PMC-2000-MAN-2025
    """
    story.append(Paragraph(support_content, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Get file info
    file_size = os.path.getsize(filename)
    
    print(f"✅ Test PDF file created: {filename}")
    print(f"   File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    print(f"   Sections: 6 chapters with comprehensive content")
    print(f"   Content: Safety, Specifications, Procedures, Maintenance, Troubleshooting, Support")
    print(f"   Features: Tables, formatted text, structured sections")
    
    return filename

if __name__ == "__main__":
    create_test_pdf()
