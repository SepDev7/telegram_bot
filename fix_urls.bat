@echo off
echo 🔧 Fixing Django URLs...
echo.

echo 📋 The issue is that Django server needs to be restarted
echo to pick up the new URL patterns.
echo.

echo 🚀 Restarting Django server...
cd cafe_bot_dashboard
python manage.py runserver 127.0.0.1:8000

echo.
echo ✅ Django server restarted!
echo 📝 Now the URLs should work with your configured server.
echo.

pause 