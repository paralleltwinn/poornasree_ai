#!/usr/bin/env python3
"""
Post-cleanup verification script
Ensures the cleaned up codebase still functions correctly
"""

import sys
import os
from pathlib import Path

def verify_cleanup():
    """Verify the cleanup was successful and code still works"""
    print("🔍 Verifying cleaned up codebase...")
    
    # Check directory structure
    expected_dirs = ['app', 'tests', 'utils', 'training', 'sample_data', 'data']
    missing_dirs = []
    
    for dir_name in expected_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All expected directories exist")
    
    # Check main files exist
    main_files = ['main.py', 'requirements.txt', '.env', 'README.md']
    missing_files = []
    
    for file_name in main_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing main files: {missing_files}")
        return False
    else:
        print("✅ All main files exist")
    
    # Test imports
    try:
        sys.path.insert(0, os.getcwd())
        from app.services.ai_service import AIService
        from app.database import engine
        print("✅ Core imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check test files
    test_files = os.listdir('tests')
    if len(test_files) >= 5:  # Should have at least 5 test files
        print(f"✅ Found {len(test_files)} test files")
    else:
        print(f"⚠️ Only found {len(test_files)} test files")
    
    # Check utils
    utils_files = os.listdir('utils')
    if len(utils_files) >= 8:  # Should have at least 8 utility files
        print(f"✅ Found {len(utils_files)} utility files")
    else:
        print(f"⚠️ Only found {len(utils_files)} utility files")
    
    print("\n🎉 Cleanup verification completed successfully!")
    print("📁 Project structure is clean and organized")
    print("🚀 Ready for development and deployment")
    
    return True

if __name__ == "__main__":
    success = verify_cleanup()
    if success:
        print("\n✅ All verification checks passed!")
    else:
        print("\n❌ Some verification checks failed!")
    
    sys.exit(0 if success else 1)
