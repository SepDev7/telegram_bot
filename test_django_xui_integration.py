import requests
import json
import uuid
import random
import string
import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

def generate_reality_keys():
    """Generate Reality keys exactly like in the Django app"""
    priv = x25519.X25519PrivateKey.generate()
    pub = priv.public_key()
    priv_b64 = base64.urlsafe_b64encode(priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )).decode().rstrip("=")
    pub_b64 = base64.urlsafe_b64encode(pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )).decode().rstrip("=")
    return priv_b64, pub_b64

def generate_unique_port(start=10000, end=60000):
    """Generate unique port"""
    return random.randint(start, end)

def generate_custom_short_ids():
    """Generate short IDs"""
    def random_hex(length):
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))
    
    pattern_lengths = [10, 8, 14, 6, 4, 2, 16, 12]
    return [random_hex(length) for length in pattern_lengths]

def generate_remark(prefix="TD"):
    """Generate remark"""
    return f"{prefix}{random.randint(100, 999)}"

def generate_random_email():
    """Generate random email"""
    local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{local_part}@example.com"

def gb_to_bytes(gb: int) -> int:
    """Convert GB to bytes"""
    return gb * 1024 * 1024 * 1024

def test_django_xui_integration():
    """Test the exact integration that Django uses"""
    
    print("🧪 Testing Django-x-ui integration...")
    print("=" * 50)
    
    # Simulate the exact payload that Django creates
    days = 30
    flow_gb = 30
    total_bytes = gb_to_bytes(flow_gb)
    client_id = str(uuid.uuid4())
    private_key, public_key = generate_reality_keys()
    
    # Create the exact payload from Django
    payload = {
        "enable": True,
        "remark": generate_remark(),
        "listen": "",
        "port": generate_unique_port(),
        "protocol": "vless",
        "expiryTime": 0,  # Simplified for test
        "settings": json.dumps({
            "clients": [{
                "id": client_id,
                "flow": "xtls-rprx-vision",
                "email": generate_random_email(),
                "tgId": None,
                "enable": True,
                "totalGB": total_bytes,
            }],
            "decryption": "none",
            "fallbacks": []
        }),
        "streamSettings": json.dumps({
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": False,
                "dest": "www.speedtest.net:443",
                "xver": 0,
                "serverNames": ["www.speedtest.net"],
                "privateKey": private_key,
                "shortIds": generate_custom_short_ids(),
                "settings": {
                    "publicKey": public_key,
                    "spiderX": "/",
                    "fingerprint": "firefox",
                }
            },
        }),
        "sniffing": json.dumps({
            "enabled": True,
            "destOverride": ["http", "tls"],
            "metadataOnly": False,
            "routeOnly": False
        })
    }
    
    print(f"🔍 Generated payload:")
    print(f"   Port: {payload['port']}")
    print(f"   Client ID: {client_id}")
    print(f"   Volume: {flow_gb} GB ({total_bytes} bytes)")
    print(f"   Duration: {days} days")
    
    try:
        # Step 1: Login to x-ui (exact same as Django)
        print("\n1. Logging into x-ui...")
        login_url = "http://localhost:3030/RZElYrcIBosloBn/login"
        login_data = {"username": "admin", "password": "admin"}
        session = requests.Session()
        
        login_response = session.post(login_url, json=login_data, timeout=10)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        print("✅ Login successful!")
        
        # Step 2: Create inbound (exact same as Django)
        print("\n2. Creating inbound...")
        api_url = "http://localhost:3030/RZElYrcIBosloBn/panel/api/inbounds/add"
        headers = {"Content-Type": "application/json"}
        
        response = session.post(api_url, headers=headers, json=payload, timeout=10)
        print(f"   API status: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    print("✅ Inbound created successfully!")
                    print(f"   Config ID: {result.get('obj', {}).get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ API returned success=false: {result.get('msg', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
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

def test_django_api_endpoint():
    """Test the Django API endpoint directly"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Django API endpoint...")
    
    # Test data similar to what the webapp sends
    test_data = {
        "telegram_id": "123456789",  # Replace with a real telegram_id from your database
        "volume": 30,
        "duration": 30,
        "description": "Test config from API"
    }
    
    try:
        # Test the Django API endpoint
        django_api_url = "https://7cbe3eb18c4b.ngrok-free.app/api/api-config-creator/"
        
        print(f"🔍 Testing Django API: {django_api_url}")
        print(f"🔍 Test data: {test_data}")
        
        response = requests.post(
            django_api_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    print("✅ Django API working correctly!")
                    return True
                else:
                    print(f"❌ Django API returned error: {result.get('msg', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Failed to parse Django API response")
                return False
        else:
            print(f"❌ Django API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Django API test failed: {e}")
        return False

if __name__ == "__main__":
    # Test x-ui integration
    xui_ok = test_django_xui_integration()
    
    # Test Django API
    django_ok = test_django_api_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 FINAL SUMMARY:")
    print(f"   x-ui integration: {'✅' if xui_ok else '❌'}")
    print(f"   Django API: {'✅' if django_ok else '❌'}")
    
    if xui_ok and not django_ok:
        print("\n🔧 ISSUE: x-ui is working but Django API is failing")
        print("   The problem is in the Django application, not x-ui")
    elif not xui_ok:
        print("\n🔧 ISSUE: x-ui integration is failing")
        print("   Check x-ui configuration and logs")
    else:
        print("\n🎉 Everything is working correctly!") 