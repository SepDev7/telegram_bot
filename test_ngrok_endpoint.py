import requests
import json
from config import BASE_URL

# Test the API endpoint
def test_ngrok_endpoint():
    url = f"{BASE_URL}/api/api-config-creator/"
    
    # Test data
    test_data = {
        "telegram_id": "123456789",
        "volume": "10",
        "duration": "7",
        "description": "Test config"
    }
    
    try:
        print(f"🔍 Testing API endpoint: {url}")
        print(f"🔍 Test data: {test_data}")
        
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        
        print(f"🔍 Status code: {response.status_code}")
        print(f"🔍 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API endpoint is working!")
        else:
            print("❌ API endpoint returned error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API endpoint. Check if the server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ngrok_endpoint() 