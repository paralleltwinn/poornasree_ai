"""
Database Configuration
====================

Database connection and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from src.core.config.settings import get_settings

settings = get_settings()

# URL encode the password to handle special characters
encoded_password = quote_plus(settings.db_password)

# Database configuration
DATABASE_URL = f"mysql+aiomysql://{settings.db_user}:{encoded_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

print(f"Database URL: mysql+aiomysql://{settings.db_user}:***@{settings.db_host}:{settings.db_port}/{settings.db_name}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
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

# Database connection testing
async def test_database_connection():
    """Test database connectivity"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# Database initialization
async def init_database():
    """Initialize database tables"""
    from src.core.models.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
