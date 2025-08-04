import os
import sys
import django

# Add the Django project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cafe_bot_dashboard'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')

# Configure Django
django.setup()

from orders.models import TelegramUser, SettlementReceipt
import requests
import json

def test_notification_system():
    """Test the notification system"""
    
    # Check for admin users
    admin_users = TelegramUser.objects.filter(role='admin')
    print(f"👥 Found {admin_users.count()} admin users:")
    for admin in admin_users:
        print(f"  - {admin.full_name} (ID: {admin.telegram_id}, Code: {admin.user_code})")
    
    if admin_users.count() == 0:
        print("❌ No admin users found! Please run setup_admin.py first.")
        return
    
    # Test sending a direct notification
    BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"
    
    def send_test_notification():
        """Send a test notification to all admins"""
        test_message = "🧪 <b>تست سیستم اعلان</b>\n\nاین یک پیام تست برای بررسی عملکرد سیستم اعلان است."
        
        for admin in admin_users:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": admin.telegram_id,
                "text": test_message,
                "parse_mode": "HTML"
            }
            try:
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Test notification sent to {admin.full_name} (ID: {admin.telegram_id})")
                else:
                    print(f"❌ Failed to send test notification to {admin.full_name}: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"❌ Error sending test notification to {admin.full_name}: {e}")
    
    # Send test notification
    print("\n🧪 Sending test notification...")
    send_test_notification()
    
    # Test creating a receipt to trigger the signal
    print("\n📝 Testing receipt creation signal...")
    try:
        # Get the first user (or create a test user)
        test_user = TelegramUser.objects.first()
        if not test_user:
            print("❌ No users found to test with!")
            return
        
        print(f"📝 Creating test receipt for user: {test_user.full_name}")
        
        # Create a test receipt (without image for testing)
        receipt = SettlementReceipt.objects.create(
            user=test_user,
            amount=1000
        )
        print(f"✅ Test receipt created with ID: {receipt.id}")
        
        # Clean up the test receipt
        receipt.delete()
        print("🧹 Test receipt cleaned up")
        
    except Exception as e:
        print(f"❌ Error testing receipt creation: {e}")

if __name__ == "__main__":
    print("🧪 Testing notification system...")
    test_notification_system()
    print("✅ Test complete!") 