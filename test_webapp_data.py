import asyncio
import json
from telegram import Update, WebAppInfo
from telegram.ext import Application, MessageHandler, filters
import os
import sys

# Add the Django project to the Python path
sys.path.append('cafe_bot_dashboard')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')

import django
django.setup()

from orders.models import TelegramUser

# Your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token

async def test_webapp_data():
    """Test function to simulate web app data"""
    print("🔍 Testing web app data handling...")
    
    # Create a mock update with web app data
    mock_data = {
        "action": "config_created",
        "config_data": {
            "type": "tunnel",
            "configType": "vless",
            "volumeType": "volume",
            "duration": "30",
            "volume": 40,
            "description": "test",
            "cost": 12000
        },
        "api_response": {
            "success": True,
            "config_id": "TD52",
            "volume": "40 GB",
            "duration": "30 روزه",
            "smart_link": "https://7cbe3eb18c4b.ngrok-free.app/user-dashboard/93147/",
            "vless_url": "vless://1fd51605-9661-4736-b336-65577af59999@localhost:50235?type=tcp&security=reality&pbk=v_lPa20IjaAI4ntv74_fIOe1dHPlzxTpQSEr0wdU5yc&fp=firefox&sni=www.speedtest.net&sid=ff06996776&spx=/&flow=xtls-rprx-vision#TD241-o9ddlkk34@example.com",
            "qr_code": "iVBORw0KGgoAAAANSUhEUgAAAa4AAAGuAQAAAADgjt83AAADJUlEQVR4nO1cUWrrMBBcSYZ+xtAD5CjOzUpvFh8lB3hgfz6w2ceutHZsUahKQuqnmQ9ViTTUgmF3tJLjmH6A2f+ERQRaBtAygJYBtAygZQAtA2gZQMsA2qFpvUug3jUUezRKo6PtbOPtCx+yFL6YoQDtS9qJBZP0/iZtCBZZkI7zdUcrhAft2LR5CRQhbY77s8hiDSgaX177kGXwhfMTQMvQ7L/obs3ERHMjGYeoG94lwBxybR60Z9F68SAXCuwuJ2bqz5NI5Vn/7XsA7bfQAjOLGEQR/NnOMbvwVVLRRbodMx90bWXwhfMroo26g2nEjaQMowKJvc9WfKzgcsS1FcKXEv5/GvEegwYUsbAn3fJos5szHWJtHrTHquQqHiTiNBFfpeEhLMoJMmXVC1RSZywZzHl0EkbUrnaxfGLa0FKJTIFKao4lnHQwxTASfawGmdjT6YglVceSYGnntKpEM44kIKm0aWhBLKmZ1sedzew0bqQqbKzVB3YfnHrU4xyn6j3OdLez4evW1kbDoqkIsaTyjEPJfgSRivnY5RjQGqik8lhCi/3QgRRGki+J8UVdLlRSG43sRkCq0HP0sTKS8sxaSEFVrXJap/40ltbk4EZ7oxwYj01KNlqwh3utmxY43VU7myIU8lEPeNzHrTnq2srgC+fXlXEoFUjYNjrbWj1qr/XSaKMSsnOceCZsskiuJRXeoJLK3Wuwxna98RwnWliNKogltZ/jsJpUk4V9XKv2Mh2xpHKac62U0cY3ji9eXHSPo1X7m7x9Idsbu9t4tLWVwBfNroJGlnG0N8Xm/jjYimxWc0MsqZBGu1tofH/+awko3i+5T0WHWJsH7UG0Jv7p7UIrpyawo/GdnSQbSTsNH29tHrSnuVda7EeMIJs7SnCvVdIa68hrWqc/ooOBXN+Gyb6ThlwaeM1DetB+G210jnlYzmzGN7tkMvyih/wWQHt4LDF0PDeOKEyuG4id7ISjJenb4WBr86A9y5dEbH2JIE2HL6mRRttfnKCNXV1f3VKVLK/nQCWV0Rx+o3EP0DKAlgG0DKBlAC0DaBlAywBaBtBoj3/TqQDSGULmrwAAAABJRU5ErkJggg==",
            "user_code": 93147
        }
    }
    
    print(f"🔍 Mock data: {json.dumps(mock_data, indent=2)}")
    
    # Import the handle_webapp_data function from main.py
    from main import handle_webapp_data
    
    # Create a mock context
    class MockContext:
        pass
    
    context = MockContext()
    
    # Create a mock message with web app data
    class MockMessage:
        def __init__(self):
            self.web_app_data = MockWebAppData()
    
    class MockWebAppData:
        def __init__(self):
            self.data = json.dumps(mock_data)
    
    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()
            self.effective_user = MockUser()
    
    class MockUser:
        def __init__(self):
            self.id = 54420628  # Use the same user ID from your test
    
    update = MockUpdate()
    
    try:
        # Call the handle_webapp_data function
        await handle_webapp_data(update, context)
        print("✅ Test completed successfully!")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_webapp_data()) 