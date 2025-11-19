@echo off
echo Setting up Product Management System...
echo.

echo 1. Installing dependencies...
pip install -r requirements.txt

echo.
echo 2. Checking environment file...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your database credentials before proceeding.
    pause
)

echo.
echo 3. Initializing database...
python reset_db.py

echo.
echo 4. Creating demo webhooks...
python create_demo_webhooks.py

echo.
echo 5. Starting application...
echo The app will be available at: http://localhost:5000
echo.
python run.py