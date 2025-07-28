#!/usr/bin/env python3
"""
Test database connection to MySQL server
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_connection():
    """Test database connection"""
    try:
        from app.database import test_database_connection, init_database
        
        print("🔄 Testing database connection...")
        
        # Test connection
        success = await test_database_connection()
        
        if success:
            print("✅ Database connection successful!")
            
            # Try to initialize database tables
            print("🔄 Initializing database tables...")
            await init_database()
            print("✅ Database tables initialized!")
            
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📋 Please install required packages:")
        print("   pip install sqlalchemy[asyncio] aiomysql pymysql alembic")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== MySQL Database Connection Test ===")
    print("Server: RDP-Main-Server")
    print("Database: psrAI")
    print("User: root")
    print("=" * 40)
    
    success = asyncio.run(test_connection())
    
    if success:
        print("\n🎉 Database setup complete!")
        print("You can now start the API server with: python main.py")
    else:
        print("\n⚠️  Database setup failed!")
        print("Please check your MySQL server connection and credentials.")
    
    input("\nPress Enter to exit...")
