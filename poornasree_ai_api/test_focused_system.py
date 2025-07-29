#!/usr/bin/env python3
"""
Test focused response system (works with or without Ollama)
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app.services.ai_service import AIService

async def test_focused_responses():
    """Test the focused response system"""
    print("🔍 Testing Focused Response System...")
    
    # Initialize AI service
    ai_service = AIService()
    await ai_service.initialize()
    
    print(f"📊 Ollama availability: {ai_service.ollama_available}")
    
    # Test different types of questions
    test_questions = [
        ("How to start the machine?", "how-to"),
        ("What is a spindle?", "definition"),
        ("Troubleshoot motor issues", "troubleshooting"),
        ("Safety precautions for operation", "safety"),
        ("Maintenance schedule", "maintenance")
    ]
    
    # Create some mock context for testing
    mock_context = [{
        'text': """
        MACHINE STARTUP PROCEDURE:
        1. Check all safety guards are in place
        2. Verify emergency stop is accessible
        3. Turn on main power switch
        4. Initialize the control system
        5. Run diagnostic checks
        6. Calibrate spindle if needed
        
        SPINDLE DEFINITION:
        The spindle is the rotating shaft that holds and drives the cutting tool.
        It provides the rotational motion needed for machining operations.
        
        MOTOR TROUBLESHOOTING:
        - Check power connections
        - Verify motor overload protection
        - Test motor windings
        - Check for mechanical binding
        
        SAFETY REQUIREMENTS:
        - Always wear safety glasses
        - Keep hands away from moving parts
        - Use proper lockout/tagout procedures
        - Never bypass safety interlocks
        
        MAINTENANCE SCHEDULE:
        - Daily: Check fluid levels, clean machine
        - Weekly: Lubricate moving parts
        - Monthly: Inspect belts and couplings
        - Quarterly: Full system inspection
        """,
        'filename': 'test_manual.pdf'
    }]
    
    print("\n" + "="*60)
    print("TESTING FOCUSED RESPONSES")
    print("="*60)
    
    for question, question_type in test_questions:
        print(f"\n📝 Question ({question_type}): {question}")
        print("-" * 50)
        
        try:
            response = ai_service._generate_focused_response(question, mock_context)
            print(f"🤖 Response:\n{response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "."*50)
    
    print("\n✅ Focused response testing complete!")
    print(f"💡 System status: {'Enhanced with AI' if ai_service.ollama_available else 'Standard focused responses'}")

if __name__ == "__main__":
    asyncio.run(test_focused_responses())
