#!/usr/bin/env python3
"""
Create psrAI database schema on MySQL server
"""
import pymysql
import sys

def create_database():
    """Create the psrAI database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='RDP-Main-Server',
            user='root',
            password='123@456',
            port=3306,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS `psrAI` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'psrAI' created successfully!")
            
            # Show existing databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📋 Available databases:")
            for db in databases:
                print(f"   - {db[0]}")
                
        connection.commit()
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_connection_to_psrai():
    """Test connection to the newly created psrAI database"""
    try:
        connection = pymysql.connect(
            host='RDP-Main-Server',
            user='root',
            password='123@456',
            database='psrAI',
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
    print("Server: RDP-Main-Server")
    print("Database: psrAI")
    print("User: root")
    print("=" * 40)
    
    # Step 1: Create database
    print("\n🔄 Step 1: Creating psrAI database...")
    if not create_database():
        print("❌ Failed to create database")
        return False
    
    # Step 2: Test connection to new database
    print("\n🔄 Step 2: Testing connection to psrAI...")
    if not test_connection_to_psrai():
        print("❌ Failed to connect to psrAI database")
        return False
    
    print("\n🎉 Database schema creation complete!")
    print("\nNext steps:")
    print("1. Run: python test_db_connection.py")
    print("2. Run: python main.py")
    
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
