#!/usr/bin/env python3
"""
🧹 Database and Knowledge Base Complete Cleanup Script
====================================================

This script will completely clean all trained data and reset the system to a fresh state:
- Clear all database tables
- Remove all uploaded files
- Delete vector embeddings and knowledge base files
- Reset AI service data
- Clean temporary files and logs

⚠️  WARNING: This action is IRREVERSIBLE!
All trained data, uploaded documents, chat history, and user data will be permanently deleted.
"""

import asyncio
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database import engine, AsyncSessionLocal
from app.models.database_models import (
    User, Document, ChatSession, ChatMessage, 
    DocumentChunk, APIUsage, SystemHealth
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cleanup.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseCleaner:
    """Complete database and knowledge base cleanup manager"""
    
    def __init__(self):
        self.project_root = project_root
        self.data_dir = self.project_root / "data"
        self.uploads_dir = self.data_dir / "uploads"
        self.knowledge_base_dir = self.data_dir / "knowledge_base"
        self.logs_dir = self.data_dir / "logs"
        self.models_dir = self.data_dir / "models"
        
        # Track cleanup statistics
        self.stats = {
            "users_deleted": 0,
            "documents_deleted": 0,
            "chat_sessions_deleted": 0,
            "chat_messages_deleted": 0,
            "document_chunks_deleted": 0,
            "api_usage_records_deleted": 0,
            "system_health_records_deleted": 0,
            "files_deleted": 0,
            "total_size_freed": 0
        }
    
    async def confirm_cleanup(self) -> bool:
        """Get user confirmation for cleanup operation"""
        print("\n" + "="*60)
        print("🚨 DATABASE AND KNOWLEDGE BASE COMPLETE CLEANUP")
        print("="*60)
        print("\n⚠️  THIS WILL PERMANENTLY DELETE:")
        print("   ✗ All user accounts and data")
        print("   ✗ All uploaded documents and files")
        print("   ✗ Complete chat history and conversations")
        print("   ✗ All trained AI models and embeddings")
        print("   ✗ Vector database and knowledge base")
        print("   ✗ API usage logs and statistics")
        print("   ✗ System health monitoring data")
        print("   ✗ Temporary files and cached data")
        
        print(f"\n📁 Directories that will be cleaned:")
        print(f"   • {self.uploads_dir}")
        print(f"   • {self.knowledge_base_dir}")
        print(f"   • {self.logs_dir}")
        print(f"   • {self.models_dir}")
        
        print(f"\n🗄️  Database tables that will be cleared:")
        print("   • users")
        print("   • documents") 
        print("   • chat_sessions")
        print("   • chat_messages")
        print("   • document_chunks")
        print("   • api_usage")
        print("   • system_health")
        
        print("\n" + "="*60)
        print("⚠️  THIS ACTION CANNOT BE UNDONE!")
        print("="*60)
        
        # Get confirmation
        while True:
            response = input("\n❓ Are you sure you want to proceed? (type 'YES' to confirm): ").strip()
            if response == "YES":
                return True
            elif response.lower() in ['no', 'n', 'exit', 'quit']:
                print("❌ Cleanup cancelled.")
                return False
            else:
                print("⚠️  Please type 'YES' to confirm or 'no' to cancel.")
    
    def calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of files in directory"""
        total_size = 0
        if directory.exists():
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, IOError):
                        pass
        return total_size
    
    def clean_directory(self, directory: Path, description: str) -> tuple[int, int]:
        """Clean a directory and return (files_deleted, size_freed)"""
        files_deleted = 0
        size_freed = 0
        
        if not directory.exists():
            logger.info(f"📁 {description}: Directory doesn't exist, skipping...")
            return files_deleted, size_freed
        
        logger.info(f"🧹 Cleaning {description}...")
        
        # Calculate size before deletion
        size_before = self.calculate_directory_size(directory)
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    try:
                        size_freed += item.stat().st_size
                        item.unlink()
                        files_deleted += 1
                        logger.debug(f"   ✓ Deleted file: {item.name}")
                    except Exception as e:
                        logger.error(f"   ✗ Failed to delete file {item.name}: {e}")
                elif item.is_dir():
                    try:
                        shutil.rmtree(item)
                        logger.debug(f"   ✓ Deleted directory: {item.name}")
                    except Exception as e:
                        logger.error(f"   ✗ Failed to delete directory {item.name}: {e}")
            
            logger.info(f"   ✅ {description}: {files_deleted} files deleted, {size_freed / (1024*1024):.2f} MB freed")
            
        except Exception as e:
            logger.error(f"   ❌ Error cleaning {description}: {e}")
        
        return files_deleted, size_freed
    
    async def clean_database_table(self, session: AsyncSession, model_class, table_name: str) -> int:
        """Clean a database table and return number of deleted records"""
        try:
            # Count records before deletion
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count_before = result.scalar()
            
            if count_before == 0:
                logger.info(f"📊 {table_name}: Already empty, skipping...")
                return 0
            
            # Delete all records
            await session.execute(text(f"DELETE FROM {table_name}"))
            
            # Reset auto increment
            await session.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))
            
            logger.info(f"   ✅ {table_name}: {count_before} records deleted")
            return count_before
            
        except Exception as e:
            logger.error(f"   ❌ Error cleaning table {table_name}: {e}")
            return 0
    
    async def clean_database(self):
        """Clean all database tables"""
        logger.info("🗄️  Starting database cleanup...")
        
        async with AsyncSessionLocal() as session:
            try:
                # Clean tables in proper order (respecting foreign key constraints)
                # Child tables first, then parent tables
                
                # API Usage (no foreign key dependencies)
                self.stats["api_usage_records_deleted"] = await self.clean_database_table(
                    session, APIUsage, "api_usage"
                )
                
                # System Health (no foreign key dependencies)
                self.stats["system_health_records_deleted"] = await self.clean_database_table(
                    session, SystemHealth, "system_health"
                )
                
                # Document Chunks (depends on documents)
                self.stats["document_chunks_deleted"] = await self.clean_database_table(
                    session, DocumentChunk, "document_chunks"
                )
                
                # Chat Messages (depends on chat_sessions and users)
                self.stats["chat_messages_deleted"] = await self.clean_database_table(
                    session, ChatMessage, "chat_messages"
                )
                
                # Chat Sessions (depends on users)
                self.stats["chat_sessions_deleted"] = await self.clean_database_table(
                    session, ChatSession, "chat_sessions"
                )
                
                # Documents (depends on users)
                self.stats["documents_deleted"] = await self.clean_database_table(
                    session, Document, "documents"
                )
                
                # Users (parent table)
                self.stats["users_deleted"] = await self.clean_database_table(
                    session, User, "users"
                )
                
                # Commit all changes
                await session.commit()
                logger.info("✅ Database cleanup completed successfully!")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Database cleanup failed: {e}")
                raise
    
    async def clean_files(self):
        """Clean all data directories and files"""
        logger.info("📁 Starting file system cleanup...")
        
        # Clean uploads directory
        files_deleted, size_freed = self.clean_directory(
            self.uploads_dir, "Uploaded Documents"
        )
        self.stats["files_deleted"] += files_deleted
        self.stats["total_size_freed"] += size_freed
        
        # Clean knowledge base directory
        files_deleted, size_freed = self.clean_directory(
            self.knowledge_base_dir, "Knowledge Base & Vector Embeddings"
        )
        self.stats["files_deleted"] += files_deleted
        self.stats["total_size_freed"] += size_freed
        
        # Clean models directory
        files_deleted, size_freed = self.clean_directory(
            self.models_dir, "AI Models & Cached Data"
        )
        self.stats["files_deleted"] += files_deleted
        self.stats["total_size_freed"] += size_freed
        
        # Clean logs directory (keep the directory but remove old logs)
        if self.logs_dir.exists():
            for log_file in self.logs_dir.glob("*.log"):
                if log_file.name != "cleanup.log":  # Keep current cleanup log
                    try:
                        size_freed = log_file.stat().st_size
                        log_file.unlink()
                        self.stats["files_deleted"] += 1
                        self.stats["total_size_freed"] += size_freed
                        logger.debug(f"   ✓ Deleted log file: {log_file.name}")
                    except Exception as e:
                        logger.error(f"   ✗ Failed to delete log file {log_file.name}: {e}")
        
        # Remove knowledge base pickle files
        for pkl_file in self.project_root.rglob("*.pkl"):
            if "knowledge_base" in pkl_file.name:
                try:
                    size_freed = pkl_file.stat().st_size
                    pkl_file.unlink()
                    self.stats["files_deleted"] += 1
                    self.stats["total_size_freed"] += size_freed
                    logger.info(f"   ✓ Deleted knowledge base file: {pkl_file}")
                except Exception as e:
                    logger.error(f"   ✗ Failed to delete {pkl_file}: {e}")
        
        logger.info("✅ File system cleanup completed!")
    
    def print_cleanup_summary(self):
        """Print detailed cleanup summary"""
        print("\n" + "="*60)
        print("📊 CLEANUP COMPLETED - SUMMARY REPORT")
        print("="*60)
        
        print(f"\n🗄️  Database Records Deleted:")
        print(f"   • Users: {self.stats['users_deleted']:,}")
        print(f"   • Documents: {self.stats['documents_deleted']:,}")
        print(f"   • Chat Sessions: {self.stats['chat_sessions_deleted']:,}")
        print(f"   • Chat Messages: {self.stats['chat_messages_deleted']:,}")
        print(f"   • Document Chunks: {self.stats['document_chunks_deleted']:,}")
        print(f"   • API Usage Records: {self.stats['api_usage_records_deleted']:,}")
        print(f"   • System Health Records: {self.stats['system_health_records_deleted']:,}")
        
        total_db_records = sum([
            self.stats['users_deleted'],
            self.stats['documents_deleted'],
            self.stats['chat_sessions_deleted'],
            self.stats['chat_messages_deleted'],
            self.stats['document_chunks_deleted'],
            self.stats['api_usage_records_deleted'],
            self.stats['system_health_records_deleted']
        ])
        
        print(f"\n📁 Files and Storage:")
        print(f"   • Files Deleted: {self.stats['files_deleted']:,}")
        print(f"   • Storage Freed: {self.stats['total_size_freed'] / (1024*1024):.2f} MB")
        
        print(f"\n✅ Total Impact:")
        print(f"   • Database Records: {total_db_records:,}")
        print(f"   • Files Removed: {self.stats['files_deleted']:,}")
        print(f"   • Disk Space Freed: {self.stats['total_size_freed'] / (1024*1024):.2f} MB")
        
        print(f"\n🎉 System Reset Complete!")
        print("   The database and knowledge base are now completely clean.")
        print("   You can start fresh with new data and training.")
        
        print("\n💡 Next Steps:")
        print("   1. Run 'python startup.py' to initialize fresh system")
        print("   2. Upload new documents to train the AI")
        print("   3. Start using the clean chatbot interface")
        
        print("="*60)
    
    async def run_cleanup(self):
        """Main cleanup orchestration method"""
        start_time = datetime.now()
        
        try:
            # Get user confirmation
            if not await self.confirm_cleanup():
                return False
            
            print(f"\n🚀 Starting complete cleanup at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Step 1: Clean database
            await self.clean_database()
            
            # Step 2: Clean files
            await self.clean_files()
            
            # Step 3: Print summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.print_cleanup_summary()
            print(f"\n⏱️  Total cleanup time: {duration.total_seconds():.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            print(f"\n❌ Cleanup failed: {e}")
            print("Check the cleanup.log file for detailed error information.")
            return False

async def main():
    """Main entry point"""
    print("🧹 Poornasree AI - Complete Database & Knowledge Base Cleanup")
    print("=" * 60)
    
    # Create cleaner instance
    cleaner = DatabaseCleaner()
    
    try:
        # Run cleanup
        success = await cleaner.run_cleanup()
        
        if success:
            print(f"\n✅ Cleanup completed successfully!")
            print("🎉 Your Poornasree AI system is now completely clean and ready for fresh data!")
        else:
            print(f"\n❌ Cleanup was cancelled or failed.")
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Cleanup interrupted by user.")
        print("⚠️  The system may be in an inconsistent state.")
        print("💡 Run the script again to complete the cleanup.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    # Run the cleanup
    asyncio.run(main())
