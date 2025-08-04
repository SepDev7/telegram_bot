#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')
django.setup()

from orders.models import TelegramUser, VlessConfig

def check_database():
    print("=== Database Check ===")
    
    # Check all users
    users = TelegramUser.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"\nUser: {user.full_name} (ID: {user.id}, Telegram ID: {user.telegram_id})")
        
        # Check configurations for this user
        configs = VlessConfig.objects.filter(user=user)
        print(f"  Configurations: {configs.count()}")
        
        for config in configs:
            print(f"    - Config ID: {config.id}, Total Bytes: {config.total_bytes}, Created: {config.created_at}")
    
    # Check all configurations
    all_configs = VlessConfig.objects.all()
    print(f"\nTotal configurations in database: {all_configs.count()}")
    
    if all_configs.count() > 0:
        print("Sample configurations:")
        for config in all_configs[:5]:  # Show first 5
            print(f"  - ID: {config.id}, User: {config.user.full_name if config.user else 'None'}, Total Bytes: {config.total_bytes}")

if __name__ == "__main__":
    check_database() 