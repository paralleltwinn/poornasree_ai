#!/usr/bin/env python3
"""
🚀 Quick Database Cleanup Script
===============================

Simple script to quickly clean all trained data from the database.
This is a lightweight version of the complete cleanup script.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database import AsyncSessionLocal
from sqlalchemy import text

async def quick_cleanup():
    """Quick database cleanup - removes all data but keeps table structure"""
    
    print("🧹 Quick Database Cleanup")
    print("=" * 30)
    print("This will delete ALL data from the database:")
    print("  • All users and their data")
    print("  • All uploaded documents") 
    print("  • All chat history")
    print("  • All trained knowledge")
    print("\n⚠️  This action cannot be undone!")
    
    # Get confirmation
    confirm = input("\nType 'YES' to proceed: ").strip()
    if confirm != "YES":
        print("❌ Cleanup cancelled.")
        return
    
    print("\n🚀 Starting cleanup...")
    
    async with AsyncSessionLocal() as session:
        try:
            # List of tables to clean (in proper order)
            tables = [
                "api_usage",
                "system_health", 
                "document_chunks",
                "chat_messages",
                "chat_sessions",
                "documents",
                "users"
            ]
            
            total_deleted = 0
            
            for table in tables:
                try:
                    # Count records
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    
                    if count > 0:
                        # Delete all records
                        await session.execute(text(f"DELETE FROM {table}"))
                        await session.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
                        print(f"  ✅ {table}: {count:,} records deleted")
                        total_deleted += count
                    else:
                        print(f"  ✓ {table}: already empty")
                        
                except Exception as e:
                    print(f"  ❌ {table}: error - {e}")
            
            # Commit changes
            await session.commit()
            
            print(f"\n✅ Cleanup completed!")
            print(f"📊 Total records deleted: {total_deleted:,}")
            print("\n💡 To also clean uploaded files, run:")
            print("   python complete_cleanup.py")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_cleanup())
