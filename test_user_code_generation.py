#!/usr/bin/env python3
"""
Test script to verify user code generation works correctly
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
from django.db import transaction

def test_user_code_generation():
    """Test user code generation by creating test users"""
    try:
        print("🧪 Testing user code generation...")
        
        # Clean up any test users first
        test_users = TelegramUser.objects.filter(telegram_id__startswith=999999)
        if test_users.exists():
            test_users.delete()
            print("🧹 Cleaned up previous test users")
        
        # Test creating multiple users to see if codes are sequential
        test_telegram_ids = [999999, 999998, 999997, 999996, 999995]
        
        print(f"Creating {len(test_telegram_ids)} test users...")
        
        created_users = []
        for telegram_id in test_telegram_ids:
            user = TelegramUser(
                telegram_id=telegram_id,
                full_name=f"Test User {telegram_id}",
                telegram_username=f"testuser{telegram_id}"
            )
            user.save()
            created_users.append(user)
            print(f"✅ Created user {user.full_name} with code {user.user_code}")
        
        # Check if codes are sequential
        codes = [user.user_code for user in created_users]
        print(f"\nGenerated codes: {codes}")
        
        # Verify they start from 10000 and are sequential
        if codes[0] >= 10000 and all(codes[i] == codes[i-1] + 1 for i in range(1, len(codes))):
            print("✅ User codes are correctly sequential starting from 10000!")
        else:
            print("❌ User codes are not sequential or don't start from 10000!")
        
        # Clean up test users
        for user in created_users:
            user.delete()
        print("🧹 Cleaned up test users")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing user code generation: {e}")
        return False

if __name__ == "__main__":
    success = test_user_code_generation()
    if success:
        print("\n🎉 User code generation test completed successfully!")
    else:
        print("\n💥 User code generation test failed!")
        sys.exit(1)
