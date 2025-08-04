import requests
import json

# Test the ngrok API endpoint
def test_ngrok_endpoint():
    url = "https://7cbe3eb18c4b.ngrok-free.app/api/api-config-creator/"
    
    # Test data
    test_data = {
        "telegram_id": "123456789",
        "volume": "10",
        "duration": "7",
        "description": "Test config"
    }
    
    try:
        print(f"🔍 Testing ngrok endpoint: {url}")
        print(f"🔍 Test data: {test_data}")
        
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        
        print(f"🔍 Status code: {response.status_code}")
        print(f"🔍 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Ngrok endpoint is working!")
        else:
            print("❌ Ngrok endpoint returned error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ngrok endpoint. Check if ngrok is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ngrok_endpoint() 