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

def create_admin_user():
    """Create an admin user for testing"""
    try:
        # Replace with your actual Telegram ID
        telegram_id = 123456789  # Replace with your Telegram ID
        full_name = "Admin User"
        username = "admin_user"
        
        # Check if user already exists
        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'full_name': full_name,
                'telegram_username': username,
                'is_verified': True,
                'role': 'admin',
                'balance': 1000  # Give admin some initial balance
            }
        )
        
        if created:
            print(f"✅ Admin user created successfully!")
            print(f"User Code: {user.user_code}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Role: {user.role}")
            print(f"Balance: {user.balance} coins")
        else:
            # Update existing user to be admin
            user.is_verified = True
            user.role = 'admin'
            user.balance = 1000
            user.save()
            print(f"✅ Existing user updated to admin!")
            print(f"User Code: {user.user_code}")
            print(f"Telegram ID: {user.telegram_id}")
            print(f"Role: {user.role}")
            print(f"Balance: {user.balance} coins")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    print("🔧 Setting up admin user...")
    create_admin_user()
    print("✅ Setup complete!") 