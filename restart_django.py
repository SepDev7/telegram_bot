import subprocess
import sys
import os
import time

def restart_django():
    """Restart Django server to pick up new URL changes"""
    
    print("🔄 Restarting Django server...")
    print("=" * 40)
    
    # Change to Django directory
    os.chdir('cafe_bot_dashboard')
    
    print("📋 Checking Django configuration...")
    try:
        # Check Django configuration
        result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Django configuration is valid")
        else:
            print("❌ Django configuration errors:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error checking Django: {e}")
        return False
    
    print("\n🚀 Starting Django server...")
    print("📝 The server will start on http://127.0.0.1:8000")
    print("🌐 Your ngrok URL should work now: https://659855601d44.ngrok-free.app")
    print("\n📋 Available URLs:")
    print("- /api/config-creator/ - Configuration creator")
    print("- /api/configs-list/ - Configurations list")
    print("- /api/admin-panel/ - Admin panel")
    print("\n🔄 Server is starting... Press Ctrl+C to stop")
    
    try:
        # Start Django server
        subprocess.run([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    restart_django() 