import requests
import json

def get_telegram_id():
    """Get Telegram ID by sending a message to the bot"""
    BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"
    
    print("🔍 To get your Telegram ID:")
    print("1. Send /start to your bot: @your_bot_username")
    print("2. Then run this script to get your ID")
    
    # Get updates from the bot
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                print(f"\n📱 Recent messages from users:")
                for update in data['result'][-5:]:  # Show last 5 updates
                    if 'message' in update:
                        message = update['message']
                        user = message.get('from', {})
                        chat_id = message.get('chat', {}).get('id')
                        first_name = user.get('first_name', '')
                        last_name = user.get('last_name', '')
                        username = user.get('username', '')
                        full_name = f"{first_name} {last_name}".strip()
                        
                        print(f"  👤 {full_name} (@{username}) - ID: {chat_id}")
                        if message.get('text') == '/start':
                            print(f"     📝 Message: {message.get('text')}")
            else:
                print("❌ No recent messages found. Please send /start to your bot first.")
        else:
            print(f"❌ Failed to get updates: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updates: {e}")

if __name__ == "__main__":
    get_telegram_id() 