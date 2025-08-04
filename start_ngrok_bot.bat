@echo off
echo 🚀 Starting Telegram Bot with Ngrok...
echo.

echo 📋 Instructions:
echo 1. Start Django server (this script will do it)
echo 2. Start ngrok: ngrok http 8000
echo 3. Update NGROK_URL in main.py with your ngrok URL
echo 4. Start the bot: python main.py
echo.

echo 🔧 Starting Django server...
cd cafe_bot_dashboard
start python manage.py runserver 127.0.0.1:8000

echo.
echo ✅ Django server started!
echo.
echo 🌐 Now start ngrok in a new terminal:
echo ngrok http 8000
echo.
echo 📝 Copy the HTTPS URL and update NGROK_URL in main.py
echo.
echo 🤖 Then start the bot:
echo python main.py
echo.

pause 