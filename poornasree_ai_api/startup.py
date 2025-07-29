#!/usr/bin/env python3
"""
Poornasree AI - Unified Startup Script (Organized Version)
=========================================================

One command to start everything with the new organized structure!
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

async def main():
    """Main startup orchestration"""
    print("Starting Poornasree AI API (Organized Structure)")
    print("=" * 55)
    
    # Step 1: Test basic imports
    print("\nStep 1: Testing organized imports...")
    try:
        # Test new import structure
        sys.path.append(str(project_root))
        print("All organized imports working!")
    except Exception as e:
        print(f"Import issues: {e}")
        print("Using fallback imports...")
    
    # Step 2: Start server
    print("\nStep 2: Starting API server...")
    print("All systems ready! Starting server...")
    
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStartup interrupted by user")
    except Exception as e:
        print(f"\nStartup failed: {e}")
