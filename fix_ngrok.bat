@echo off
echo 🚀 Fixing Server Setup...
echo.

echo 📋 Current Status:
echo - The bot is configured to use your server settings
echo - Make sure your server is running and accessible
echo.

echo 🔧 To fix this:
echo.

echo 1. Check your config.py file:
echo    - SERVER_DOMAIN should be your domain or IP
echo    - SERVER_IP should be your server IP
echo    - XUI_PORT should be your x-ui panel port
echo.

echo 2. Start Django server (in a new terminal):
echo    cd cafe_bot_dashboard
echo    python manage.py runserver 127.0.0.1:8000
echo.

echo 3. Make sure your server is accessible:
echo    - Check if your domain/IP is reachable
echo    - Verify x-ui panel is running
echo.

echo 4. Start the bot:
echo    python main.py
echo.

echo 💡 Quick fix - Update config.py:
echo Edit config.py and update your server settings:
echo - SERVER_DOMAIN = "your-domain.com"
echo - SERVER_IP = "your-server-ip"
echo.

pause 