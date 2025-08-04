import subprocess
import sys
import re
import time

def check_server_config():
    """Check if the server configuration is properly set up"""
    try:
        from config import SERVER_DOMAIN, SERVER_IP, XUI_PORT
        print(f"✅ Server configuration found:")
        print(f"   - SERVER_DOMAIN: {SERVER_DOMAIN}")
        print(f"   - SERVER_IP: {SERVER_IP}")
        print(f"   - XUI_PORT: {XUI_PORT}")
        return True
    except ImportError:
        print("❌ config.py not found")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def test_server_connectivity():
    """Test if the server is accessible"""
    try:
        from config import SERVER_DOMAIN, SERVER_IP
        import requests
        
        # Test domain connectivity
        try:
            response = requests.get(f"https://{SERVER_DOMAIN}", timeout=5)
            print(f"✅ Domain {SERVER_DOMAIN} is accessible")
            return True
        except:
            print(f"❌ Domain {SERVER_DOMAIN} is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False

def main():
    print("🚀 Server Configuration Helper")
    print("=" * 40)
    
    print("\n📋 Instructions:")
    print("1. Make sure your server is running and accessible")
    print("2. Update config.py with your server details")
    print("3. Start Django server: cd cafe_bot_dashboard && python manage.py runserver")
    print("4. Start the bot: python main.py")
    
    print("\n🔍 Checking server configuration...")
    config_ok = check_server_config()
    
    if config_ok:
        print("\n🔍 Testing server connectivity...")
        connectivity_ok = test_server_connectivity()
        
        if connectivity_ok:
            print("\n🎉 Server configuration is ready!")
            print("You can now start the bot: python main.py")
        else:
            print("\n❌ Server is not accessible")
            print("Please check:")
            print("- Your server is running")
            print("- Domain/IP is correct in config.py")
            print("- Firewall settings")
    else:
        print("\n❌ Server configuration is missing")
        print("Please run: python setup_server.py")

if __name__ == "__main__":
    main() 