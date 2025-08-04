import requests
import json

def test_xui_login():
    """Test the x-ui login endpoint"""
    login_url = "http://localhost:3030/RZElYrcIBosloBn/login"
    login_data = {"username": "admin", "password": "admin"}
    
    print(f"🔍 Testing x-ui login endpoint: {login_url}")
    print(f"🔍 Login data: {login_data}")
    
    try:
        # Test basic connectivity first
        print("\n1. Testing basic connectivity...")
        response = requests.get("http://localhost:3030", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
        
        # Test the login endpoint
        print("\n2. Testing login endpoint...")
        session = requests.Session()
        login_response = session.post(login_url, json=login_data, timeout=10)
        
        print(f"   Status Code: {login_response.status_code}")
        print(f"   Headers: {dict(login_response.headers)}")
        print(f"   Response Text: {login_response.text[:500]}...")
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_xui_api_endpoint():
    """Test the x-ui API endpoint for adding inbounds"""
    api_url = "http://localhost:3030/RZElYrcIBosloBn/panel/api/inbounds/add"
    
    print(f"\n3. Testing API endpoint: {api_url}")
    
    try:
        # First try to login
        session = requests.Session()
        login_url = "http://localhost:3030/RZElYrcIBosloBn/login"
        login_data = {"username": "admin", "password": "admin"}
        
        login_response = session.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Cannot test API - login failed: {login_response.status_code}")
            return False
        
        # Test the API endpoint with a simple request
        test_payload = {
            "enable": False,  # Set to False to avoid creating actual config
            "remark": "TEST_CONFIG",
            "listen": "",
            "port": 12345,
            "protocol": "vless",
            "expiryTime": 0,
            "settings": json.dumps({
                "clients": [{
                    "id": "test-id",
                    "flow": "",
                    "email": "test@example.com",
                    "enable": True,
                    "totalGB": 1073741824,  # 1 GB
                }],
                "decryption": "none",
                "fallbacks": []
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "none",
                "tcpSettings": {
                    "header": {
                        "type": "none"
                    }
                }
            }),
            "sniffing": json.dumps({
                "enabled": True,
                "destOverride": ["http", "tls"]
            })
        }
        
        headers = {"Content-Type": "application/json"}
        response = session.post(api_url, headers=headers, json=test_payload, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        if response.status_code in [200, 400, 422]:  # These are expected responses
            print("✅ API endpoint is responding!")
            return True
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_port_connectivity():
    """Test if port 3030 is open and listening"""
    import socket
    
    print("\n4. Testing port 3030 connectivity...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 3030))
        sock.close()
        
        if result == 0:
            print("✅ Port 3030 is open and listening")
            return True
        else:
            print(f"❌ Port 3030 is not accessible (error code: {result})")
            return False
            
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing x-ui API connectivity...")
    print("=" * 50)
    
    # Test port connectivity
    port_ok = test_port_connectivity()
    
    # Test login endpoint
    login_ok = test_xui_login()
    
    # Test API endpoint
    api_ok = test_xui_api_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"   Port 3030 accessible: {'✅' if port_ok else '❌'}")
    print(f"   Login endpoint working: {'✅' if login_ok else '❌'}")
    print(f"   API endpoint working: {'✅' if api_ok else '❌'}")
    
    if not port_ok:
        print("\n🔧 RECOMMENDATION: x-ui service is not running on port 3030")
        print("   Please start the x-ui service:")
        print("   - If using WSL: sudo systemctl start x-ui")
        print("   - If using Docker: docker start <x-ui-container>")
        print("   - Check if x-ui is installed: /usr/local/x-ui/x-ui status")
    
    elif not login_ok:
        print("\n🔧 RECOMMENDATION: x-ui is running but login is failing")
        print("   - Check username/password")
        print("   - Check x-ui logs: sudo journalctl -u x-ui -f")
    
    elif not api_ok:
        print("\n🔧 RECOMMENDATION: Login works but API endpoint is failing")
        print("   - Check x-ui configuration")
        print("   - Check API permissions")
    
    else:
        print("\n🎉 All tests passed! x-ui is working correctly.") 