import subprocess
import sys
import re
import time

def get_ngrok_url():
    """Get the ngrok URL from the ngrok process"""
    try:
        # Check if ngrok is running
        result = subprocess.run(['ngrok', 'api', 'tunnels'], capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if data['tunnels']:
                return data['tunnels'][0]['public_url']
    except:
        pass
    return None

def update_bot_config(ngrok_url):
    """Update the NGROK_URL in main.py"""
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the placeholder URL with the actual ngrok URL
        updated_content = re.sub(
            r'NGROK_URL = "https://your-ngrok-url\.ngrok\.io"',
            f'NGROK_URL = "{ngrok_url}"',
            content
        )
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated main.py with ngrok URL: {ngrok_url}")
        return True
    except Exception as e:
        print(f"❌ Error updating main.py: {e}")
        return False

def main():
    print("🚀 Ngrok Setup Helper")
    print("=" * 40)
    
    print("\n📋 Instructions:")
    print("1. Start Django server: cd cafe_bot_dashboard && python manage.py runserver 127.0.0.1:8000")
    print("2. In a new terminal, start ngrok: ngrok http 8000")
    print("3. Copy the HTTPS URL from ngrok (e.g., https://abc123.ngrok.io)")
    print("4. Run this script again to update the bot configuration")
    
    print("\n🔍 Checking for running ngrok...")
    ngrok_url = get_ngrok_url()
    
    if ngrok_url:
        print(f"✅ Found ngrok URL: {ngrok_url}")
        if update_bot_config(ngrok_url):
            print("\n🎉 Setup complete!")
            print("Now you can start the bot: python main.py")
        else:
            print("\n❌ Failed to update bot configuration")
    else:
        print("❌ No ngrok tunnel found")
        print("\n📝 Manual setup:")
        print("1. Start ngrok: ngrok http 8000")
        print("2. Copy the HTTPS URL")
        print("3. Edit main.py and replace 'https://f94ada0a5e4d.ngrok-free.app' with your actual URL")

if __name__ == "__main__":
    main() 