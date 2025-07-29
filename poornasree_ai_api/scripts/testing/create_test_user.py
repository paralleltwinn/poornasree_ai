#!/usr/bin/env python3
"""
Create a test user for testing the enhanced AI training system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.database_models import User
from sqlalchemy import select
import uuid

async def create_test_user():
    """Create a test user for testing"""
    print("🔧 Creating test user...")
    
    # Get database session
    async with AsyncSessionLocal() as db:
        try:
            # Check if test user already exists
            result = await db.execute(select(User).filter(User.user_id == "test_user"))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Test user already exists!")
                return
            
            # Create test user
            test_user = User(
                user_id="test_user",
                name="Test User",
                email="test@example.com"
            )
            
            db.add(test_user)
            await db.commit()
            
            print("✅ Test user created successfully!")
            print(f"   User ID: {test_user.user_id}")
            print(f"   Name: {test_user.name}")
            print(f"   Email: {test_user.email}")
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_test_user())
