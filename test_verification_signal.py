#!/usr/bin/env python3
"""
Test script for verification signal system
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

def test_verification_signal():
    """Test the verification signal system"""
    
    try:
        # Find any user to test with
        user = TelegramUser.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"🧪 Testing verification signal for user: {user.full_name}")
        print(f"📱 Telegram ID: {user.telegram_id}")
        print(f"🆔 User Code: {user.user_code}")
        print(f"✅ Current verified status: {user.is_verified}")
        
        # Test 1: Toggle verification status (this should trigger the signal)
        print("\n🔄 Test 1: Toggling verification status...")
        user.is_verified = not user.is_verified
        user.save()
        
        print(f"✅ Verification status toggled to: {user.is_verified}")
        
        # Test 2: Toggle back (this should also trigger the signal if going from True to False)
        print("\n🔄 Test 2: Toggling verification status back...")
        user.is_verified = not user.is_verified
        user.save()
        
        print(f"✅ Verification status toggled back to: {user.is_verified}")
        
        print("\n📱 Check your Telegram bot to see if notifications were sent!")
        print("🔔 You should see signal messages in the console above.")
        
    except Exception as e:
        print(f"❌ Error testing verification signal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_verification_signal()
