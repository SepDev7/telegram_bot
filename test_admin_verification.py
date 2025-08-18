#!/usr/bin/env python3
"""
Test script for admin verification process
"""

import os
import sys
import django

# Add the Django project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cafe_bot_dashboard'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')

# Configure Django
django.setup()

from orders.models import TelegramUser

def test_admin_verification():
    """Test the admin verification process"""
    
    try:
        # Find an unverified user
        unverified_user = TelegramUser.objects.filter(is_verified=False).first()
        
        if not unverified_user:
            print("❌ No unverified users found")
            return
        
        print(f"🧪 Testing verification for user: {unverified_user.full_name}")
        print(f"📱 Telegram ID: {unverified_user.telegram_id}")
        print(f"🆔 User Code: {unverified_user.user_code}")
        print(f"✅ Current verified status: {unverified_user.is_verified}")
        
        # Simulate admin verification (this will trigger the notification)
        print("\n🔄 Simulating admin verification...")
        unverified_user.is_verified = True
        unverified_user.save()
        
        print(f"✅ User verified successfully!")
        print(f"✅ New verified status: {unverified_user.is_verified}")
        
        # Check if notification was sent (you should see it in the Telegram bot)
        print("\n📱 Check your Telegram bot to see if the notification was sent!")
        
    except Exception as e:
        print(f"❌ Error testing admin verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_verification()
