@echo off
echo 🚀 Starting Telegram Bot with Server Configuration...
echo.

echo 📋 Instructions:
echo 1. Start Django server (this script will do it)
echo 2. Make sure your server is configured in config.py
echo 3. Start the bot: python main.py
echo.

echo 🔧 Starting Django server...
cd cafe_bot_dashboard
start python manage.py runserver 127.0.0.1:8000

echo.
echo ✅ Django server started!
echo.
echo 🌐 Make sure your server is accessible:
echo - Check config.py for correct SERVER_DOMAIN and SERVER_IP
echo - Verify x-ui panel is running
echo.
echo 🤖 Then start the bot:
echo python main.py
echo.

pause 