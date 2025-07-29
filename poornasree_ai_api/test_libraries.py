#!/usr/bin/env python3
"""
Test script to verify all required libraries are working correctly
"""

print("🔍 Testing Library Availability...")
print("="*50)

# Test PDF libraries
try:
    import pdfplumber
    print("✅ pdfplumber imported successfully")
except ImportError as e:
    print(f"❌ pdfplumber failed: {e}")

try:
    import pypdf
    print("✅ pypdf imported successfully")  
except ImportError as e:
    print(f"❌ pypdf failed: {e}")

try:
    import PyPDF2
    print("✅ PyPDF2 imported successfully")
except ImportError as e:
    print(f"❌ PyPDF2 failed: {e}")

# Test Excel libraries
try:
    import openpyxl
    print("✅ openpyxl imported successfully")
except ImportError as e:
    print(f"❌ openpyxl failed: {e}")

try:
    import xlrd
    print("✅ xlrd imported successfully")
except ImportError as e:
    print(f"❌ xlrd failed: {e}")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
except ImportError as e:
    print(f"❌ pandas failed: {e}")

# Test AI libraries
try:
    import sentence_transformers
    print("✅ sentence_transformers imported successfully")
except ImportError as e:
    print(f"❌ sentence_transformers failed: {e}")

try:
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
except ImportError as e:
    print(f"❌ google.generativeai failed: {e}")

print("="*50)
print("🎉 Library test completed!")
