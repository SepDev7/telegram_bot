import requests
import json

def test_fixed_endpoint():
    """Test the API with the correct ngrok URL"""
    
    # Use a real user from the database
    test_data = {
        "telegram_id": "54420628",  # Real user from database
        "volume": 10,
        "duration": 7,
        "description": "Test config after fix"
    }
    
    # Use the correct ngrok URL
    url = "https://7cbe3eb18c4b.ngrok-free.app/api/api-config-creator/"
    
    print("🧪 Testing fixed endpoint...")
    print(f"🔍 URL: {url}")
    print(f"🔍 Data: {test_data}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("🎉 SUCCESS! Config creation is working!")
                print(f"   Config ID: {result.get('config_id', 'N/A')}")
                print(f"   Smart Link: {result.get('smart_link', 'N/A')}")
                return True
            else:
                print(f"❌ API returned error: {result.get('msg', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_endpoint()
    
    if success:
        print("\n🎉 PROBLEM SOLVED!")
        print("The 'ساخت کانفیگ' functionality should now work correctly.")
        print("The issue was the wrong ngrok URL in the webapp template.")
    else:
        print("\n❌ Still having issues. Please check Django logs.") 