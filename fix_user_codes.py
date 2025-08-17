#!/usr/bin/env python3
"""
Script to fix user codes and ensure they follow sequential pattern starting from 10000
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

def fix_user_codes():
    """Fix user codes to ensure sequential numbering starting from 10000"""
    try:
        with transaction.atomic():
            # Get all users ordered by creation time (or ID as fallback)
            users = TelegramUser.objects.all().order_by('id')
            
            if not users.exists():
                print("No users found in database.")
                return
            
            print(f"Found {users.count()} users. Starting to fix user codes...")
            
            # Start from 10000
            next_code = 10000
            
            for user in users:
                old_code = user.user_code
                user.user_code = next_code
                user.save(update_fields=['user_code'])
                
                print(f"User {user.full_name} (ID: {user.telegram_id}): {old_code} → {next_code}")
                next_code += 1
            
            print(f"\n✅ Successfully fixed user codes for {users.count()} users!")
            print(f"Next available user code: {next_code}")
            
    except Exception as e:
        print(f"❌ Error fixing user codes: {e}")
        raise

def check_user_codes():
    """Check current user codes and identify any issues"""
    try:
        users = TelegramUser.objects.all().order_by('user_code')
        
        if not users.exists():
            print("No users found in database.")
            return
        
        print(f"Current user codes for {users.count()} users:")
        print("-" * 50)
        
        expected_code = 10000
        issues_found = False
        
        for user in users:
            if user.user_code != expected_code:
                print(f"❌ User {user.full_name}: Expected {expected_code}, got {user.user_code}")
                issues_found = True
            else:
                print(f"✅ User {user.full_name}: {user.user_code}")
            
            expected_code += 1
        
        if not issues_found:
            print("\n✅ All user codes are correctly sequential!")
        else:
            print("\n❌ Issues found with user codes. Run fix_user_codes() to resolve.")
            
    except Exception as e:
        print(f"❌ Error checking user codes: {e}")

if __name__ == "__main__":
    print("🔍 Checking current user codes...")
    check_user_codes()
    
    print("\n" + "="*60)
    
    response = input("\nDo you want to fix the user codes? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🔧 Fixing user codes...")
        fix_user_codes()
        
        print("\n" + "="*60)
        print("🔍 Verifying fix...")
        check_user_codes()
    else:
        print("No changes made.")
