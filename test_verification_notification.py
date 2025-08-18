#!/usr/bin/env python3
"""
Test script for user verification notifications
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
from orders.notifications import send_verification_notification

def test_verification_notification():
    """Test sending verification notification to a user"""
    
    # Find a test user (you can modify this to use a specific user)
    try:
        user = TelegramUser.objects.first()
        if user:
            print(f"🧪 Testing verification notification for user: {user.full_name}")
            print(f"📱 Telegram ID: {user.telegram_id}")
            print(f"🆔 User Code: {user.user_code}")
            
            # Send test notification
            success = send_verification_notification(user)
            
            if success:
                print("✅ Verification notification sent successfully!")
            else:
                print("❌ Failed to send verification notification")
        else:
            print("❌ No users found in database")
            
    except Exception as e:
        print(f"❌ Error testing notification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_verification_notification()
