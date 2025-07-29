#!/usr/bin/env python3
"""
Database initialization script for Poornasree AI
Creates MySQL tables with proper compatibility for strict mode
"""
import asyncio
import sys
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal

# SQL statements for creating tables with MySQL-compatible syntax
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS `users` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `user_id` VARCHAR(100) NOT NULL UNIQUE,
        `name` VARCHAR(255) NULL,
        `email` VARCHAR(255) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME NULL,
        PRIMARY KEY (`id`),
        INDEX `ix_users_id` (`id`),
        INDEX `ix_users_user_id` (`user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `documents` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `document_id` VARCHAR(100) NOT NULL UNIQUE,
        `user_id` VARCHAR(100) NOT NULL,
        `filename` VARCHAR(500) NOT NULL,
        `original_filename` VARCHAR(500) NOT NULL,
        `file_type` VARCHAR(50) NOT NULL,
        `file_size` INTEGER NOT NULL,
        `file_path` VARCHAR(1000) NOT NULL,
        `description` TEXT NULL,
        `content_text` TEXT NULL,
        `processing_status` VARCHAR(50) DEFAULT 'pending',
        `chunk_count` INTEGER DEFAULT 0,
        `vector_embeddings_path` VARCHAR(1000) NULL,
        `processing_time` FLOAT NULL,
        `doc_metadata` TEXT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME NULL,
        PRIMARY KEY (`id`),
        INDEX `ix_documents_id` (`id`),
        INDEX `ix_documents_document_id` (`document_id`),
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `chat_sessions` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `session_id` VARCHAR(100) NOT NULL UNIQUE,
        `user_id` VARCHAR(100) NOT NULL,
        `title` VARCHAR(500) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` DATETIME NULL,
        PRIMARY KEY (`id`),
        INDEX `ix_chat_sessions_id` (`id`),
        INDEX `ix_chat_sessions_session_id` (`session_id`),
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `chat_messages` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `message_id` VARCHAR(100) NOT NULL UNIQUE,
        `session_id` VARCHAR(100) NOT NULL,
        `user_id` VARCHAR(100) NOT NULL,
        `message_text` TEXT NOT NULL,
        `response_text` TEXT NULL,
        `is_user_message` BOOLEAN DEFAULT TRUE,
        `confidence_score` FLOAT NULL,
        `processing_time` FLOAT NULL,
        `source_documents` TEXT NULL,
        `doc_metadata` TEXT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        INDEX `ix_chat_messages_id` (`id`),
        INDEX `ix_chat_messages_message_id` (`message_id`),
        FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`session_id`),
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `document_chunks` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `chunk_id` VARCHAR(100) NOT NULL UNIQUE,
        `document_id` VARCHAR(100) NOT NULL,
        `chunk_index` INTEGER NOT NULL,
        `chunk_text` TEXT NOT NULL,
        `chunk_size` INTEGER NOT NULL,
        `embedding_vector` TEXT NULL,
        `chunk_metadata` TEXT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        INDEX `ix_document_chunks_id` (`id`),
        INDEX `ix_document_chunks_chunk_id` (`chunk_id`),
        FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `api_usage` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `user_id` VARCHAR(100) NOT NULL,
        `endpoint` VARCHAR(200) NOT NULL,
        `method` VARCHAR(10) NOT NULL,
        `status_code` INTEGER NOT NULL,
        `processing_time` FLOAT NULL,
        `request_size` INTEGER NULL,
        `response_size` INTEGER NULL,
        `ip_address` VARCHAR(45) NULL,
        `user_agent` VARCHAR(500) NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        INDEX `ix_api_usage_id` (`id`),
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS `system_health` (
        `id` INTEGER NOT NULL AUTO_INCREMENT,
        `metric_name` VARCHAR(100) NOT NULL,
        `metric_value` FLOAT NOT NULL,
        `metric_unit` VARCHAR(50) NULL,
        `status` VARCHAR(20) NOT NULL,
        `system_metadata` TEXT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        INDEX `ix_system_health_id` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

async def create_database_tables():
    """Create all database tables with MySQL-compatible syntax"""
    try:
        print("🔄 Creating database tables...")
        
        async with engine.begin() as conn:
            for i, sql in enumerate(CREATE_TABLES_SQL, 1):
                try:
                    table_name = sql.split('`')[1]  # Extract table name
                    print(f"   Creating table {i}/7: {table_name}")
                    await conn.execute(text(sql))
                    print(f"   ✅ Table {table_name} created successfully")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠️  Table {table_name} already exists - skipping")
                    else:
                        print(f"   ❌ Error creating table {table_name}: {e}")
                        raise
        
        print("\n✅ All database tables created successfully!")
        
        # Verify tables exist
        print("\n🔍 Verifying table creation...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['users', 'documents', 'chat_sessions', 'chat_messages', 
                             'document_chunks', 'api_usage', 'system_health']
            
            print(f"📊 Found {len(tables)} tables in database:")
            for table in sorted(tables):
                status = "✅" if table in expected_tables else "❓"
                print(f"   {status} {table}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print(f"\n🎉 All required tables are present!")
                return True
                
    except Exception as e:
        print(f"\n❌ Failed to create database tables: {e}")
        return False

async def check_database_connection():
    """Check if database connection is working"""
    try:
        print("🔄 Testing database connection...")
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main function to initialize database"""
    print("=== Poornasree AI Database Setup ===")
    print("Database: MySQL (psrAI)")
    print("Server: RDP-Main-Server")
    print("=" * 40)
    
    # Check connection first
    if not await check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Create tables
    success = await create_database_tables()
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the API server: python main.py")
        print("2. Test document upload: python train_documents.py")
        print("3. Access the API docs: http://localhost:8000/docs")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
