import os
import sys
import django

# Add the Django project to the Python path
sys.path.append('cafe_bot_dashboard')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')
django.setup()

from orders.models import TelegramUser
from config import BASE_URL
import requests
import json

def check_users_and_test():
    # Check users in database
    users = TelegramUser.objects.all()
    print(f"🔍 Found {users.count()} users in database:")
    
    for user in users[:5]:  # Show first 5 users
        print(f"  - ID: {user.id}, Telegram ID: {user.telegram_id}, Name: {user.full_name}, Balance: {user.balance}")
    
    if users.exists():
        # Test with the first user
        test_user = users.first()
        print(f"\n🔍 Testing with user: {test_user.telegram_id}")
        
        # Test the endpoint
        url = f"{BASE_URL}/api/api-config-creator/"
        test_data = {
            "telegram_id": str(test_user.telegram_id),
            "volume": "10",
            "duration": "7",
            "description": "Test config"
        }
        
        try:
            print(f"🔍 Testing endpoint: {url}")
            print(f"🔍 Test data: {test_data}")
            
            response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
            
            print(f"🔍 Status code: {response.status_code}")
            print(f"🔍 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Endpoint is working!")
            else:
                print("❌ Endpoint returned error")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No users found in database")

if __name__ == "__main__":
    check_users_and_test() 