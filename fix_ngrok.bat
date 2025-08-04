@echo off
echo 🚀 Fixing Ngrok Setup...
echo.

echo 📋 Current Status:
echo - The bot is trying to use: your-ngrok-url.ngrok.io
echo - This URL is offline because ngrok is not running
echo.

echo 🔧 To fix this:
echo.
echo 1. Start Django server (in a new terminal):
echo    cd cafe_bot_dashboard
echo    python manage.py runserver 127.0.0.1:8000
echo.
echo 2. Start ngrok (in another new terminal):
echo    ngrok http 8000
echo.
echo 3. Copy the HTTPS URL from ngrok output
echo    (e.g., https://abc123.ngrok.io)
echo.
echo 4. Update main.py with the real URL:
echo    python setup_ngrok.py
echo.
echo 5. Start the bot:
echo    python main.py
echo.

echo 💡 Quick fix - Manual URL update:
echo Edit main.py and change line 18:
echo NGROK_URL = "https://f94ada0a5e4d.ngrok-free.app"
echo to your actual ngrok URL
echo.

pause 