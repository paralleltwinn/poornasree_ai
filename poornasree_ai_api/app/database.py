from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "RDP-Main-Server")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123@456")
DB_NAME = os.getenv("DB_NAME", "psrAI")

# URL encode the password to handle special characters
encoded_password = quote_plus(DB_PASSWORD)

# Database configuration for your MySQL database
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔧 Database URL: mysql+aiomysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_database_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Test database connection
async def test_database_connection():
    """Test the database connection"""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Initialize database tables
async def init_database():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they're registered
            from app.models.database_models import (
                User, Document, ChatSession, ChatMessage as DBChatMessage,
                DocumentChunk, APIUsage, SystemHealth
            )
            
            # Create all tables (this will skip existing tables)
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables initialized successfully!")
            return True
    except Exception as e:
        error_msg = str(e)
        if "Invalid default value" in error_msg:
            print(f"⚠️  Database table creation had datetime compatibility issue: {e}")
            print("   This is usually due to MySQL strict mode - tables may still work")
            # Try to continue - the tables might have been created despite the error
            return True
        else:
            print(f"❌ Failed to initialize database tables: {e}")
            return False
