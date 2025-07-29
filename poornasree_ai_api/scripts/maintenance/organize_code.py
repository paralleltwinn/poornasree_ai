#!/usr/bin/env python3
"""
Code Organization and Cleanup Script for Poornasree AI API
This script will:
1. Move test files to tests/ directory
2. Move utility scripts to utils/ directory
3. Move training files to training/ directory
4. Remove duplicate and unnecessary files
5. Clean up the project structure
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_and_organize():
    """Main cleanup function"""
    base_dir = Path(__file__).parent
    
    print("🧹 Starting code cleanup and organization...")
    print(f"📁 Working directory: {base_dir}")
    
    # Define file categorization
    test_files_to_move = [
        "test_*.py",
        "verify_*.py"
    ]
    
    utility_files_to_move = [
        "create_database.py",
        "create_database_tables.py", 
        "clear_training_data.py",
        "setup_mysql.bat",
        "start.bat",
        "create_test_*.py",
        "pdf_accuracy_enhancer.py"
    ]
    
    training_files_to_move = [
        "train_*.py",
        "enhanced_service_guide_trainer.py",
        "trained_service_guide_*.json",
        "trained_service_guide_*.pdf"
    ]
    
    sample_data_files = [
        "test_*.pdf",
        "test_*.xlsx", 
        "test_*.txt",
        "enhanced_cnc_manual.pdf",
        "Training syllabus and documents.xlsx"
    ]
    
    # Files to delete (duplicates and unnecessary)
    files_to_delete = [
        # These are duplicate Gemini test files - keeping the most comprehensive one
        "test_complete_gemini.py",  # Duplicate of test_gemini_complete_integration.py
        "test_gemini_2_5_flash_lite_complete.py",  # Duplicate functionality
        "test_focused_system.py",  # Has issues, functionality covered by other tests
        "test_flutter_gemini_chat.py",  # Specific test, covered by integration tests
        "test_fixed_gemini_service.py",  # Development test, no longer needed
        "verify_gemini_fix.py",  # Development test, no longer needed
        
        # Duplicate PDFs
        "trained_service_guide_test_cnc_manual.pdf",  # Duplicate
        "trained_service_guide_enhanced_cnc_manual.pdf",  # Duplicate
    ]
    
    print("\n📦 Moving files to organized directories...")
    
    # Move test files
    tests_dir = base_dir / "tests"
    for pattern in test_files_to_move:
        for file_path in glob.glob(str(base_dir / pattern)):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                if filename not in files_to_delete:
                    dest = tests_dir / filename
                    print(f"  📝 {filename} → tests/")
                    shutil.move(file_path, dest)
    
    # Move utility files
    utils_dir = base_dir / "utils"
    for pattern in utility_files_to_move:
        for file_path in glob.glob(str(base_dir / pattern)):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest = utils_dir / filename
                print(f"  🔧 {filename} → utils/")
                shutil.move(file_path, dest)
    
    # Move training files
    training_dir = base_dir / "training"
    for pattern in training_files_to_move:
        for file_path in glob.glob(str(base_dir / pattern)):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest = training_dir / filename
                print(f"  🎓 {filename} → training/")
                shutil.move(file_path, dest)
    
    # Move sample data files
    sample_data_dir = base_dir / "sample_data"
    for pattern in sample_data_files:
        for file_path in glob.glob(str(base_dir / pattern)):
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest = sample_data_dir / filename
                print(f"  📄 {filename} → sample_data/")
                shutil.move(file_path, dest)
    
    print("\n🗑️  Removing duplicate and unnecessary files...")
    
    # Delete unnecessary files
    for filename in files_to_delete:
        file_path = base_dir / filename
        if file_path.exists():
            print(f"  ❌ Deleting {filename}")
            file_path.unlink()
    
    # Clean up __pycache__ directories
    for pycache_dir in glob.glob(str(base_dir / "**/__pycache__"), recursive=True):
        print(f"  🧹 Removing {pycache_dir}")
        shutil.rmtree(pycache_dir)
    
    print("\n📁 Creating __init__.py files for Python packages...")
    
    # Create __init__.py files for proper Python packages
    for directory in [tests_dir, utils_dir, training_dir]:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Python package\n")
            print(f"  ✅ Created {directory.name}/__init__.py")
    
    print("\n✅ Code cleanup and organization completed!")
    print("\n📂 New project structure:")
    print("  📁 app/          - Main application code")
    print("  📁 tests/        - All test files")
    print("  📁 utils/        - Utility scripts and tools")
    print("  📁 training/     - AI training scripts and data")
    print("  📁 sample_data/  - Sample files for testing")
    print("  📁 data/         - Runtime data and knowledge base")
    print("  📄 main.py       - FastAPI application entry point")
    print("  📄 requirements.txt - Python dependencies")
    print("  📄 .env          - Environment configuration")

if __name__ == "__main__":
    cleanup_and_organize()
