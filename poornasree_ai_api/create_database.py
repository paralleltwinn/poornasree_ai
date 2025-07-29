#!/usr/bin/env python3
"""
Create psrAI database schema on MySQL server
"""
import pymysql
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the psrAI database if it doesn't exist"""
    # Get database configuration from environment variables
    DB_HOST = os.getenv("DB_HOST", "RDP-Main-Server")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123@456")
    DB_NAME = os.getenv("DB_NAME", "psrAI")
    
    print(f"🔧 Using database configuration:")
    print(f"   Host: {DB_HOST}")
    print(f"   Port: {DB_PORT}")
    print(f"   User: {DB_USER}")
    print(f"   Database: {DB_NAME}")
    print()
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{DB_NAME}' created successfully!")
            
            # Show existing databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📋 Available databases:")
            for db in databases:
                print(f"   - {db[0]}")
                
        connection.commit()
        connection.close()
        return True, DB_HOST, DB_PORT, DB_USER, DB_NAME
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False, None, None, None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None, None, None, None

def test_connection_to_psrai():
    """Test connection to the newly created psrAI database"""
    # Get database configuration from environment variables
    DB_HOST = os.getenv("DB_HOST", "RDP-Main-Server")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123@456")
    DB_NAME = os.getenv("DB_NAME", "psrAI")
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=3306,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"✅ Successfully connected to database: {current_db[0]}")
            
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ Connection to psrAI failed: {e}")
        return False

def main():
    print("=== Creating psrAI Database Schema ===")
    
    # Load database configuration
    DB_HOST = os.getenv("DB_HOST", "RDP-Main-Server")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_NAME = os.getenv("DB_NAME", "psrAI")
    
    print(f"Server: {DB_HOST}:{DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print("=" * 40)
    
    # Step 1: Create database
    print("\n🔄 Step 1: Creating database...")
    success, host, port, user, db_name = create_database()
    if not success:
        print("❌ Failed to create database")
        return False
    
    # Step 2: Test connection to new database
    print(f"\n🔄 Step 2: Testing connection to {db_name}...")
    if not test_connection_to_psrai():
        print(f"❌ Failed to connect to {db_name} database")
        return False
    
    print("\n🎉 Database schema creation complete!")
    print("\nNext steps:")
    print("1. Run: python create_database_tables.py")
    print("2. Run: python test_db_connection.py")
    print("3. Run: python main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except ImportError:
        print("❌ pymysql not installed.")
        print("Install with: pip install pymysql")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    
    input("\nPress Enter to exit...")
