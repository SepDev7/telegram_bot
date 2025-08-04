import asyncio
import json
import sys
import os

# Add the Django project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cafe_bot_dashboard'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')

# Configure Django
import django
django.setup()

from main import handle_webapp_data

async def test_simple_webapp_data():
    """Test if the webapp data handler is working with simple data"""
    
    # Create a simple mock update
    class MockWebAppData:
        def __init__(self):
            self.data = json.dumps({
                "action": "config_created",
                "config_data": {"test": "data"},
                "api_response": {
                    "success": True,
                    "config_id": "TEST123",
                    "volume": "50 GB",
                    "duration": "30 روزه",
                    "smart_link": "https://test.com",
                    "vless_url": "vless://test",
                    "qr_code": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                }
            })
    
    class MockMessage:
        def __init__(self):
            self.web_app_data = MockWebAppData()
        
        async def reply_text(self, text, **kwargs):
            print(f"📤 Bot would send: {text}")
            return True
        
        async def reply_photo(self, photo, **kwargs):
            print(f"📤 Bot would send photo with caption: {kwargs.get('caption', 'No caption')}")
            return True
    
    class MockUser:
        def __init__(self):
            self.id = 123456789
    
    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()
            self.effective_user = MockUser()
    
    class MockContext:
        pass
    
    print("🧪 Testing simple webapp data handler...")
    
    try:
        update = MockUpdate()
        context = MockContext()
        
        await handle_webapp_data(update, context)
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_simple_webapp_data()) 