@echo off
echo Installing MySQL database dependencies for Poornasree AI API...
echo.

echo Step 1: Installing Python dependencies...
pip install sqlalchemy==2.0.23
pip install aiomysql==0.2.0
pip install pymysql==1.1.0
pip install alembic==1.13.1

echo.
echo Step 2: Installing existing dependencies...
pip install -r requirements.txt

echo.
echo Step 3: Testing database connection...
python -c "
import asyncio
import aiomysql

async def test_connection():
    try:
        conn = await aiomysql.connect(
            host='RDP-Main-Server',
            port=3306,
            user='root',
            password='123@456',
            db='psrapp'
        )
        print('✅ Database connection successful!')
        conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        print('Please check:')
        print('1. MySQL server is running on RDP-Main-Server')
        print('2. Database psrapp exists')
        print('3. User root has access with password 123@456')
        print('4. Port 3306 is accessible')

asyncio.run(test_connection())
"

echo.
echo ✅ MySQL setup complete!
echo.
echo To start the API with database support:
echo python main.py
echo.
pause
