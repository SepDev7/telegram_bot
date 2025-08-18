from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Order, Cart, MenuItem, TelegramUser
from .serializers import OrderSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import TelegramUser, Configuration, SettlementReceipt, ConfigReport
import json
from django.views.decorators.http import require_GET, require_POST
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q
import requests
import time
from orders.models import TelegramUser, VlessConfig
from django.utils.timezone import make_aware
from datetime import datetime, timedelta, timezone
import string
from urllib.parse import quote
import uuid
import base64
import urllib.parse
import random
import secrets
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization

# Import configuration from Django settings
from django.conf import settings
SERVER_DOMAIN = settings.SERVER_DOMAIN
SERVER_IP = settings.SERVER_IP
XUI_PORT = settings.XUI_PORT
XUI_PATH = settings.XUI_PATH
XUI_USERNAME = settings.XUI_USERNAME
XUI_PASSWORD = settings.XUI_PASSWORD
BASE_URL = settings.BASE_URL
XUI_BASE_URL = settings.XUI_BASE_URL
WEBAPP_BASE_URL = settings.WEBAPP_BASE_URL


class CheckVerificationView(APIView):
    def get(self, request):
        telegram_id = request.GET.get('telegram_id')
        if not telegram_id:
            return Response({"error": "Missing telegram_id"}, status=400)

        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if user:
            role = user.role

            return Response({
                "user_code": user.user_code,
                "is_verified": user.is_verified,
                "role": role
            })
        return Response({"error": "User not found"}, status=404)


class RegisterUserView(APIView):
    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        full_name = request.data.get("full_name")
        username = request.data.get("telegram_username", "")

        if not telegram_id or not full_name:
            return Response({"error": "Missing required fields"}, status=400)

        existing = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if existing:
            role = existing.role

            return Response({
                "user_code": existing.user_code,
                "is_verified": existing.is_verified,
                "role": role
            })

        # Create user instance first to trigger custom save method
        user = TelegramUser(
            telegram_id=telegram_id,
            full_name=full_name,
            telegram_username=username,
        )
        # Save to trigger the custom save method which generates sequential user_code
        user.save()

        # Role creation is now handled by model signal
        return Response({
            "user_code": user.user_code,
            "is_verified": user.is_verified,
            "role": "customer"
        })


class CreateOrderView(APIView):
    def post(self, request):
        print("🚨 Request data:", request.data)

        item_id = request.data.get('item')
        item = MenuItem.objects.filter(id=item_id).first()
        if not item:
            return Response({'error': 'Item not found'}, status=400)

        cart, _ = Cart.objects.get_or_create(
            telegram_username=request.data.get('telegram_username', ''),
            defaults={
                'customer_name': request.data.get('customer_name'),
                'telegram_username': request.data.get('telegram_username', '')
            }
        )

        order = Order.objects.create(cart=cart, item=item)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)


class CartView(APIView):
    def get(self, request):
        tg_id = request.GET.get('telegram_username')
        cart = Cart.objects.filter(telegram_username=tg_id).first()
        if not cart:
            return Response([], status=200)
        orders = cart.orders.filter(status='new')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class RemoveOrderView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        order = Order.objects.filter(id=order_id).first()
        if order:
            order.delete()
            return Response({"removed": True})
        return Response({"error": "Order not found"}, status=404)


def telegram_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        telegram_id = request.GET.get('telegram_id')
        if not telegram_id:
            return HttpResponseForbidden("No telegram_id provided.")
        user = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
        if not user:
            return HttpResponseForbidden("You are not an admin.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_panel(request):
    telegram_id = request.GET.get('telegram_id')
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            if user.role == 'admin':
                # Get all users for the admin panel
                users = TelegramUser.objects.all().order_by('-id')
                return render(request, 'orders/admin_panel.html', {
                    'user': user,
                    'users': users
                })
        except TelegramUser.DoesNotExist:
            pass
    return JsonResponse({'error': 'Unauthorized'}, status=403)

def admin_webapp(request):
    telegram_id = request.GET.get('user_id')
    user = None
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    return render(request, 'orders/admin_webapp.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

def config_creator(request):
    """Serve the configuration creator web app"""
    telegram_id = request.GET.get('user_id')
    user = None
    
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    
    return render(request, 'orders/config_creator.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

def configs_list(request):
    """Serve the configurations list web app"""
    telegram_id = request.GET.get('user_id')
    user = None
    configs = []
    
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
            
            # Get user's VlessConfig records
            vless_configs = VlessConfig.objects.filter(user=user).order_by('-created_at')
            
            # Convert to template-friendly format
            for config in vless_configs:
                gb_value = round(config.total_bytes / (1024**3), 1)  # Convert bytes to GB
                
                # Handle missing fields gracefully
                try:
                    used_bytes = getattr(config, 'used_bytes', 0)
                    used_gb = round(used_bytes / (1024**3), 1)
                except:
                    used_gb = 0
                
                try:
                    is_active = getattr(config, 'is_active', True)
                except:
                    is_active = True
                
                try:
                    expires_at = getattr(config, 'expires_at', None)
                    if expires_at:
                        from django.utils import timezone
                        remaining = expires_at - timezone.now()
                        days_remaining = max(0, remaining.days)
                    else:
                        days_remaining = None
                except:
                    days_remaining = None
                
                # Calculate usage percentage
                usage_percentage = 0
                if config.total_bytes > 0:
                    usage_percentage = min(100, (used_bytes / config.total_bytes) * 100)
                
                config_data = {
                    'id': config.id,
                    'name': f"TD{config.id}",
                    'status': 'active' if is_active else 'inactive',
                    'data_used': used_gb,
                    'data_total': gb_value,
                    'vless_url': config.vless_url,
                    'created_at': config.created_at.isoformat() if config.created_at else None,
                    'gb_value': gb_value,
                    'usage_percentage': usage_percentage,
                    'days_remaining': days_remaining,
                    'is_expired': False if days_remaining is None else days_remaining <= 0
                }
                configs.append(config_data)
                
        except TelegramUser.DoesNotExist:
            pass
        except Exception as e:
            pass
    
    # Serialize configs to JSON for the template
    configs_json = json.dumps(configs, ensure_ascii=False)
    
    return render(request, 'orders/configs_list.html', {
        'user': user,
        'user_balance': user.balance if user else 0,
        'configs': configs_json,
        'profile_picture_url': user.profile_picture.url if user and user.profile_picture else None
    })

def settings_panel(request):
    """Serve the settings web app"""
    telegram_id = request.GET.get('user_id')
    user = None
    
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    
    return render(request, 'orders/settings.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

def settlement_webapp(request):
    telegram_id = request.GET.get('user_id')
    user = None
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    return render(request, 'orders/settlement.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

def wallet_to_wallet_webapp(request):
    telegram_id = request.GET.get('user_id')
    user = None
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    return render(request, 'orders/wallet_to_wallet.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

def rules_webapp(request):
    telegram_id = request.GET.get('user_id')
    user = None
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            pass
    return render(request, 'orders/rules.html', {
        'user': user,
        'user_balance': user.balance if user else 0
    })

@csrf_exempt
def webapp_data_handler(request):
    """Handle data from the web app"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data.get('user_id')
            config_data = data.get('config_data')
            
            if telegram_id and config_data:
                user = TelegramUser.objects.get(telegram_id=telegram_id)
                
                # Create configuration
                config = Configuration.objects.create(
                    user=user,
                    name=f"کانفیگ {user.user_code}_{config_data.get('type', 'custom')}",
                    description=config_data.get('description', ''),
                    is_active=True
                )
                
                # Deduct balance
                cost = config_data.get('cost', 0)
                if user.balance >= cost:
                    user.balance -= cost
                    user.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'کانفیگ با موفقیت ایجاد شد',
                        'config_id': config.id,
                        'remaining_balance': user.balance
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'موجودی کافی نیست'
                    }, status=400)
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در ایجاد کانفیگ: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def create_inbound(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')
            user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
            if not user:
                return JsonResponse({'success': False, 'msg': 'User not found'}, status=404)

            # Extract user inputs from data
            volume = data.get('volume')
            duration = data.get('duration')
            description = data.get('description')

            now = datetime.now()
            expiry_datetime = now + timedelta(days=int(duration))
            expiry_ms = int(expiry_datetime.timestamp() * 1000)
            total_bytes = gb_to_bytes(int(volume))
            client_id = str(uuid.uuid4())
            private_key, public_key = generate_reality_keys()

            payload = {
                "enable": True,
                "remark": generate_remark(user_code=user.user_code),
                "listen": "",
                "port": generate_unique_port(),
                "protocol": "vless",
                "expiryTime": expiry_ms,
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

            # ✅ Login to x-ui 
            login_url = f"{XUI_BASE_URL}/{XUI_PATH}/login"
            login_data = {"username": XUI_USERNAME, "password": XUI_PASSWORD}
            session = requests.Session()
            login_response = session.post(login_url, json=login_data)

            if login_response.status_code != 200:
                return JsonResponse({
                    "success": False,
                    "msg": "Login to x-ui failed",
                    "login_response": login_response.text
                }, status=401)

            # ✅ Post inbound config
            api_url = f"{XUI_BASE_URL}/{XUI_PATH}/panel/api/inbounds/add"
            headers = {"Content-Type": "application/json"}
            response = session.post(api_url, headers=headers, json=payload)
            content_type = response.headers.get("Content-Type", "")

            if 'application/json' in content_type:
                try:
                    api_result = response.json()
                except json.JSONDecodeError:
                    return JsonResponse({
                        "success": False,
                        "msg": "Failed to decode JSON from x-ui response",
                        "raw_response": response.text
                    }, status=502)
            else:
                return JsonResponse({
                    "success": False,
                    "msg": "x-ui did not return JSON",
                    "content_type": content_type,
                    "raw_response": response.text
                }, status=502)

            # ✅ Add VLESS URL to result and save to database
            if api_result.get("success") and api_result.get("obj"):
                api_result["vless_url"] = generate_vless_url(api_result["obj"])
                print("✅ VLESS URL:", api_result["vless_url"])

                # Create VlessConfig record
                from django.utils import timezone
                from datetime import timedelta
                
                # Calculate expiration date based on duration
                expires_at = timezone.now() + timedelta(days=int(duration))
                
                # Get the remark from the payload for the name field
                config_name = payload.get('remark', f'TD{api_result["obj"].get("id", "unknown")}')
                
                vless_config = VlessConfig.objects.create(
                    user=user,
                    vless_url=api_result["vless_url"],
                    name=config_name,  # Save the config name/remark
                    total_bytes=total_bytes,
                    expires_at=expires_at,
                )

                # Prepare response data for Telegram bot
                config_id = api_result["obj"].get("id", "TD" + str(vless_config.id))
                config_name = f"TD{config_id}"
                
                # Generate smart link (user dashboard URL)
                smart_link = f"{WEBAPP_BASE_URL}/api/user-dashboard/{user.user_code}/"
                
                # Create QR code for smart link
                import qrcode
                import base64
                from io import BytesIO
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(smart_link)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

                # Return success response with all necessary data
                response_data = {
                    "success": True,
                    "config_id": config_name,
                    "volume": f"{volume} GB",
                    "duration": f"{duration} روزه" if int(duration) == 1 else f"{duration} روزه",
                    "smart_link": smart_link,
                    "vless_url": api_result["vless_url"],
                    "qr_code": qr_code_base64,
                    "user_code": user.user_code
                }
                print(f"🔍 Returning success response: {response_data}")
                return JsonResponse(response_data)

            return JsonResponse(api_result, status=response.status_code)

        except Exception as e:
            return JsonResponse({"success": False, "msg": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)

def generate_reality_keys():
    priv = X25519PrivateKey.generate()
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

used_ports = set()

def generate_unique_port(start=10000, end=60000):
    for _ in range(100):  # Try up to 100 random ports
        port = random.randint(start, end)
        if port not in used_ports:
            used_ports.add(port)
            return port
    raise Exception("No available port found in range.")


def generate_custom_short_ids():
    def random_hex(length):
        return ''.join(secrets.choice('0123456789abcdef') for _ in range(length))

    pattern_lengths = [10, 8, 14, 6, 4, 2, 16, 12]
    return [random_hex(length) for length in pattern_lengths]

def generate_remark(user_code=None, prefix="T"):
    if user_code:
        return f"{prefix}{user_code}"
    else:
        return f"{prefix}{random.randint(100, 999)}"

def generate_random_email():
    local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{local_part}@example.com"

def gb_to_bytes(gb: int) -> int:
    """
    Convert gigabytes (GB) to bytes using binary conversion.
    1 GB = 1024^3 = 1,073,741,824 bytes
    """
    return gb * 1024 * 1024 * 1024


def generate_vless_url(obj):
    try:
        settings = json.loads(obj["settings"])
        stream_settings = json.loads(obj["streamSettings"])

        client = settings["clients"][0]
        client_id = client["id"]
        email = client["email"]
        port = obj["port"]
        remark = obj["remark"]

        network = stream_settings["network"]
        security = stream_settings["security"]
        reality = stream_settings["realitySettings"]

        pbk = reality["settings"]["publicKey"]
        fp = reality["settings"]["fingerprint"]
        sni = reality["serverNames"][0]
        sid = reality["shortIds"][0]
        spx = urllib.parse.quote(reality["settings"]["spiderX"])
        flow = client.get("flow", "")

        return (
            f"vless://{client_id}@{SERVER_DOMAIN}:{port}"
            f"?type={network}&security={security}"
            f"&pbk={pbk}&fp={fp}&sni={sni}&sid={sid}&spx={spx}&flow={flow}"
            f"#{remark}-{email}"
        )
    except Exception as e:
        return f"error-generating-url: {str(e)}"

@csrf_exempt
def api_config_creator(request):
    print(f"🔍 API Config Creator called with method: {request.method}")
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        print(f"🔍 Received data: {data}")
        telegram_id = data.get('telegram_id')  # Changed from user_id to telegram_id
        print(f"🔍 Telegram ID: {telegram_id}")
        
        # Get user first to check balance
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return JsonResponse({"success": False, "msg": "User not found."}, status=404)
        
        # Calculate cost based on volume and duration
        days = data.get("duration")
        days = int(days)
        flow_gb = int(data.get("volume", 30))  # default to 30 GB
        
        # Cost calculation: base cost * duration multiplier * volume multiplier
        base_cost = 1000  # Base cost in coins
        duration_multiplier = days
        volume_multiplier = flow_gb / 10  # Every 10 GB adds to the cost
        total_cost = int(base_cost * duration_multiplier * volume_multiplier)
        
        print(f"🔍 Cost calculation: base={base_cost}, duration={days}, volume={flow_gb}GB, total_cost={total_cost}")
        
        # Check if user has enough balance
        if user.balance < total_cost:
            return JsonResponse({
                "success": False, 
                "msg": f"موجودی ناکافی! هزینه مورد نیاز: {total_cost} سکه، موجودی شما: {user.balance} سکه. لطفاً ابتدا موجودی خود را افزایش دهید.",
                "required_balance": total_cost,
                "current_balance": user.balance
            }, status=400)
        
        now = datetime.now()
        expiry_datetime = now + timedelta(days=days)
        expiry_ms = int(expiry_datetime.timestamp() * 1000)
        description = data.get('description', 'New inbound')
        total_bytes = gb_to_bytes(flow_gb)
        expiry_time = 30
        client_id = str(uuid.uuid4())
        private_key, public_key = generate_reality_keys()

        payload = {
            "enable": True,
            "remark": generate_remark(user_code=user.user_code),
            "listen": "",
            "port": generate_unique_port(),
            "protocol": "vless",
            "expiryTime": expiry_ms,
            "settings": json.dumps({
                "clients": [{
                    "id": client_id,
                    "flow": "xtls-rprx-vision",
                    "email": generate_random_email(),
                    "tgId": user.user_code,
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

        # ✅ Login to x-ui
        login_url = f"{XUI_BASE_URL}/{XUI_PATH}/login"
        login_data = {"username": XUI_USERNAME, "password": XUI_PASSWORD}
        session = requests.Session()
        print(f"🔍 Trying to login to x-ui at: {login_url}")
        login_response = session.post(login_url, json=login_data)
        print(f"🔍 Login response status: {login_response.status_code}")
        print(f"🔍 Login response text: {login_response.text}")

        if login_response.status_code != 200:
            print(f"❌ X-UI login failed with status {login_response.status_code}")
            return JsonResponse({
                "success": False,
                "msg": "Login to x-ui failed",
                "login_response": login_response.text
            }, status=401)

        # ✅ Post inbound config
        api_url = f"{XUI_BASE_URL}/{XUI_PATH}/panel/api/inbounds/add"
        headers = {"Content-Type": "application/json"}
        response = session.post(api_url, headers=headers, json=payload)
        content_type = response.headers.get("Content-Type", "")

        if 'application/json' in content_type:
            try:
                api_result = response.json()
            except json.JSONDecodeError:
                return JsonResponse({
                    "success": False,
                    "msg": "Failed to decode JSON from x-ui response",
                    "raw_response": response.text
                }, status=502)
        else:
            return JsonResponse({
                "success": False,
                "msg": "x-ui did not return JSON",
                "content_type": content_type,
                "raw_response": response.text
            }, status=502)

        # ✅ Add VLESS URL to result and save to database
        if api_result.get("success") and api_result.get("obj"):
            api_result["vless_url"] = generate_vless_url(api_result["obj"])
            print("✅ VLESS URL:", api_result["vless_url"])

            # Create VlessConfig record
            from django.utils import timezone
            
            # Calculate expiration date based on duration
            expires_at = timezone.now() + timedelta(days=days)
            
            # Get the remark from the payload for the name field
            config_name = payload.get('remark', f'TD{api_result["obj"].get("id", "unknown")}')
            
            vless_config = VlessConfig.objects.create(
                user=user,
                vless_url=api_result["vless_url"],
                name=config_name,  # Save the config name/remark
                total_bytes=total_bytes,
                expires_at=expires_at,
            )

            # Deduct cost from user's balance
            user.balance -= total_cost
            user.save()
            print(f"✅ Deducted {total_cost} coins from user {user.telegram_id}. New balance: {user.balance}")

            # Prepare response data for Telegram bot
            config_id = api_result["obj"].get("id", "TD" + str(vless_config.id))
            config_name = f"TD{config_id}"
            
            # Generate smart link (user dashboard URL)
            smart_link = f"{WEBAPP_BASE_URL}/api/user-dashboard/{user.user_code}/"
            
            # Create QR code for smart link
            import qrcode
            import base64
            from io import BytesIO
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(smart_link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Return success response with all necessary data
            response_data = {
                "success": True,
                "config_id": config_name,
                "volume": f"{flow_gb} GB",
                "duration": f"{days} روزه" if days == 1 else f"{days} روزه",
                "smart_link": smart_link,
                "vless_url": api_result["vless_url"],
                "qr_code": qr_code_base64,
                "user_code": user.user_code,
                "user_balance": user.balance,
                "cost_paid": total_cost
            }
            print(f"🔍 Returning success response: {response_data}")
            return JsonResponse(response_data)

        return JsonResponse(api_result, status=response.status_code)

    except Exception as e:
        return JsonResponse({"success": False, "msg": str(e)}, status=500)


@telegram_admin_required
def toggle_verify(request, user_id):
    user = get_object_or_404(TelegramUser, id=user_id)
    was_verified = user.is_verified
    user.is_verified = not user.is_verified
    user.save()
    
    # Send notification if user was just verified
    if user.is_verified and not was_verified:
        from .notifications import send_verification_notification
        send_verification_notification(user)
    
    return JsonResponse({'success': True, 'is_verified': user.is_verified})

@telegram_admin_required
def toggle_role(request, user_id):
    user = get_object_or_404(TelegramUser, id=user_id)
    user.role = 'admin' if user.role == 'customer' else 'customer'
    user.save()
    return JsonResponse({'success': True, 'role': user.role})

@require_GET
def admin_users_list(request):
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset
    users = TelegramUser.objects.all()
    
    # Apply search filter if query exists
    if search_query:
        # Search by name, telegram_id, or user_code
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(telegram_id__icontains=search_query) |
            Q(user_code__icontains=search_query)
        )
    
    users = users.order_by('-id')
    
    data = [
        {
            'id': u.id,
            'code': u.user_code,
            'name': u.full_name,
            'telegram_id': u.telegram_id,
            'verified': u.is_verified,
            'role': u.role,
            'balance': u.balance,
        } for u in users
    ]
    return JsonResponse({'users': data})

@csrf_exempt
@require_POST
def admin_user_verify(request):
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        user = TelegramUser.objects.get(id=user_id)
        was_verified = user.is_verified
        user.is_verified = not user.is_verified
        user.save()
        
        # Send notification if user was just verified
        if user.is_verified and not was_verified:
            from .notifications import send_verification_notification
            send_verification_notification(user)
        
        return JsonResponse({'success': True, 'verified': user.is_verified})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def admin_user_role(request):
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        user = TelegramUser.objects.get(id=user_id)
        user.role = 'admin' if user.role == 'customer' else 'customer'
        user.save()
        return JsonResponse({'success': True, 'role': user.role})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def admin_user_delete(request):
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        user = TelegramUser.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def admin_user_balance(request):
    """Admin endpoint to edit user balance"""
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        user_id = data.get('id')
        new_balance = data.get('balance')
        
        if new_balance is None or not isinstance(new_balance, (int, float)):
            return JsonResponse({'error': 'Invalid balance value'}, status=400)
        
        user = TelegramUser.objects.get(id=user_id)
        old_balance = user.balance
        user.balance = new_balance
        user.save()
        
        return JsonResponse({
            'success': True, 
            'old_balance': old_balance,
            'new_balance': new_balance,
            'user_name': user.full_name
        })
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def upload_settlement_receipt(request):
    user_id = request.POST.get('user_id')
    amount = request.POST.get('amount')
    image = request.FILES.get('receipt')
    if not user_id or not amount or not image:
        return JsonResponse({'success': False, 'message': 'اطلاعات ناقص است.'}, status=400)
    try:
        user = TelegramUser.objects.get(telegram_id=user_id)
        print(f"📝 Creating receipt for user {user.full_name} (ID: {user.telegram_id}) with amount {amount}")
        receipt = SettlementReceipt.objects.create(
            user=user,
            amount=amount,
            image=image
        )
        print(f"✅ Receipt created successfully with ID: {receipt.id}")
        return JsonResponse({'success': True, 'message': 'رسید با موفقیت ثبت شد.'})
    except TelegramUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'کاربر یافت نشد.'}, status=404)
    except Exception as e:
        print(f"❌ Error creating receipt: {e}")
        return JsonResponse({'success': False, 'message': f'خطا: {str(e)}'}, status=500)

@csrf_exempt
@require_GET
def admin_receipts_list(request):
    telegram_id = request.GET.get('user_id')
    admin = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
    if not admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    receipts = SettlementReceipt.objects.filter(is_verified=False).order_by('-created_at')
    data = [
        {
            'id': r.id,
            'user': r.user.full_name,
            'user_code': r.user.user_code,
            'amount': r.amount,
            'image_url': r.image.url if r.image else '',
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
            'edited_amount': r.edited_amount,
        } for r in receipts
    ]
    return JsonResponse({'receipts': data})

@csrf_exempt
@require_POST
def verify_receipt(request):
    try:
        data = json.loads(request.body)
        receipt_id = data.get('id')
        amount = int(data.get('amount'))
        admin_id = data.get('user_id')
        admin = TelegramUser.objects.filter(telegram_id=admin_id, role='admin').first()
        if not admin:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        receipt = SettlementReceipt.objects.get(id=receipt_id)
        if receipt.is_verified:
            return JsonResponse({'success': False, 'message': 'این رسید قبلاً تایید شده است.'}, status=400)
        user = receipt.user
        # Update amount if edited
        if amount != receipt.amount:
            receipt.edited_amount = amount
        receipt.is_verified = True
        receipt.verified_by = admin
        from django.utils import timezone
        receipt.verified_at = timezone.now()
        receipt.save()
        # Add to user balance
        user.balance += amount
        user.save()
        return JsonResponse({'success': True, 'message': 'رسید تایید و مبلغ به موجودی افزوده شد.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'خطا: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def wallet_to_wallet_transfer(request):
    try:
        data = json.loads(request.body)
        sender_id = data.get('user_id')
        recipient_code = data.get('recipient_code')
        amount = int(data.get('amount'))
        if not sender_id or not recipient_code or not amount:
            return JsonResponse({'success': False, 'message': 'اطلاعات ناقص است.'}, status=400)
        sender = TelegramUser.objects.filter(telegram_id=sender_id).first()
        recipient = TelegramUser.objects.filter(user_code=recipient_code).first()
        if not sender:
            return JsonResponse({'success': False, 'message': 'کاربر ارسال کننده یافت نشد.'}, status=404)
        if not recipient:
            return JsonResponse({'success': False, 'message': 'کد پنل مقصد یافت نشد.'}, status=404)
        if sender.balance < amount:
            return JsonResponse({'success': False, 'message': 'موجودی کافی نیست.'}, status=400)
        if amount <= 0:
            return JsonResponse({'success': False, 'message': 'مبلغ انتقالی باید بیشتر از صفر باشد.'}, status=400)
        with transaction.atomic():
            sender.balance -= amount
            recipient.balance += amount
            sender.save()
            recipient.save()
        return JsonResponse({'success': True, 'message': 'انتقال با موفقیت انجام شد.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'خطا: {str(e)}'}, status=500)


def user_dashboard(request, user_code):
    """User dashboard view for displaying configuration details"""
    try:
        # Convert user_code to integer since it's stored as PositiveIntegerField
        user_code_int = int(user_code)
        user = TelegramUser.objects.get(user_code=user_code_int)
        configs = VlessConfig.objects.filter(user=user).order_by('-created_at')
        
        # Calculate GB for each config
        configs_with_gb = []
        for config in configs:
            gb_value = round(config.total_bytes / (1024**3), 1)
            used_gb = round(config.used_bytes / (1024**3), 1)
            remaining_gb = round(config.get_remaining_bytes() / (1024**3), 1)
            days_remaining = config.get_days_remaining()
            
            configs_with_gb.append({
                'config': config,
                'gb_value': gb_value,
                'used_gb': used_gb,
                'remaining_gb': remaining_gb,
                'usage_percentage': config.get_usage_percentage(),
                'days_remaining': days_remaining,
                'is_expired': config.is_expired(),
                'is_active': config.is_active
            })
        
        context = {
            'user': user,
            'configs': configs,
            'configs_with_gb': configs_with_gb,
            'ngrok_url': BASE_URL,
            'profile_picture_url': user.profile_picture.url if user.profile_picture else None
        }
        
        return render(request, 'orders/user_dashboard.html', context)
        
    except (ValueError, TelegramUser.DoesNotExist):
        return JsonResponse({"error": "User not found"}, status=404)

@csrf_exempt
@require_POST
def toggle_config_status(request):
    """Toggle configuration status (active/inactive)"""
    try:
        data = json.loads(request.body)
        config_id = data.get('config_id')
        telegram_id = data.get('telegram_id')
        
        if not config_id or not telegram_id:
            return JsonResponse({"success": False, "message": "Missing required parameters"}, status=400)
        
        # Get user and verify ownership
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        config = VlessConfig.objects.get(id=config_id, user=user)
        
        # For now, we'll just return success since we don't have an is_active field
        # In the future, you might want to add an is_active field to VlessConfig model
        return JsonResponse({
            "success": True, 
            "message": "وضعیت کانفیگ تغییر کرد",
            "new_status": "active"  # All configs are considered active for now
        })
        
    except (TelegramUser.DoesNotExist, VlessConfig.DoesNotExist):
        return JsonResponse({"success": False, "message": "کانفیگ یا کاربر یافت نشد"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطا: {str(e)}"}, status=500)

@csrf_exempt
@require_POST
def delete_config(request):
    """Delete a configuration"""
    try:
        data = json.loads(request.body)
        config_id = data.get('config_id')
        telegram_id = data.get('telegram_id')
        
        if not config_id or not telegram_id:
            return JsonResponse({"success": False, "message": "Missing required parameters"}, status=400)
        
        # Get user and verify ownership
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        config = VlessConfig.objects.get(id=config_id, user=user)
        
        # Delete the configuration
        config.delete()
        
        return JsonResponse({
            "success": True, 
            "message": "کانفیگ با موفقیت حذف شد"
        })
        
    except (TelegramUser.DoesNotExist, VlessConfig.DoesNotExist):
        return JsonResponse({"success": False, "message": "کانفیگ یا کاربر یافت نشد"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطا: {str(e)}"}, status=500)

@csrf_exempt
@require_POST
def upload_profile_picture(request):
    """Upload profile picture for user"""
    try:
        telegram_id = request.POST.get('telegram_id')
        profile_picture = request.FILES.get('profile_picture')
        
        if not telegram_id or not profile_picture:
            return JsonResponse({"success": False, "message": "Missing required parameters"}, status=400)
        
        # Get user
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        
        # Save the profile picture
        user.profile_picture = profile_picture
        user.save()
        
        return JsonResponse({
            "success": True, 
            "message": "عکس پروفایل با موفقیت آپلود شد",
            "profile_picture_url": user.profile_picture.url if user.profile_picture else None
        })
        
    except TelegramUser.DoesNotExist:
        return JsonResponse({"success": False, "message": "کاربر یافت نشد"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"خطا: {str(e)}"}, status=500)

def external_configs_list(request):
    """
    Get configs from database and enrich with usage data from external API.
    """
    user_code = request.GET.get('user_code')
    print(f"🔍 External configs requested for user_code: {user_code}")
    if not user_code:
        return JsonResponse({'success': False, 'message': 'user_code is required'}, status=400)

    # Get user and their configs from database
    try:
        from .models import TelegramUser, VlessConfig
        user = TelegramUser.objects.get(user_code=user_code)
        print(f"🔍 Found user: {user.full_name}")
        
        # Get all configs for this user from database
        db_configs = VlessConfig.objects.filter(user=user)
        print(f"🔍 Found {db_configs.count()} configs in database")
        
        if not db_configs.exists():
            return JsonResponse({
                'success': True, 
                'configs': [],
                'message': 'No configs found in database'
            })
            
    except TelegramUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        print(f"❌ Error getting user/configs: {e}")
        return JsonResponse({'success': False, 'message': 'Database error'}, status=500)

    # Login to x-ui first
    try:
        login_url = f"{XUI_BASE_URL}/{XUI_PATH}/login"
        login_data = {
            "username": XUI_USERNAME,
            "password": XUI_PASSWORD
        }
        
        session = requests.Session()
        login_response = session.post(login_url, json=login_data)
        print(f"🔍 Login response status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return JsonResponse({
                'success': False, 
                'message': 'Failed to login to external API',
                'login_response': login_response.text
            }, status=500)
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return JsonResponse({'success': False, 'message': 'Login error'}, status=500)

    # Get configs from external API
    try:
        api_url = f"{XUI_BASE_URL}/{XUI_PATH}/panel/api/inbounds/list"
        api_response = session.get(api_url)
        print(f"🔍 API response status: {api_response.status_code}")
        
        if api_response.status_code != 200:
            print(f"❌ API call failed: {api_response.text}")
            return JsonResponse({
                'success': False, 
                'message': 'Failed to get configs from external API',
                'api_response': api_response.text
            }, status=500)
            
        data = api_response.json()
        print(f"🔍 API returned {len(data.get('obj', []))} configs")
        
    except Exception as e:
        print(f"❌ API call error: {e}")
        return JsonResponse({'success': False, 'message': 'API call error'}, status=500)

    # Process and match configs
    combined_configs = []
    now = datetime.now(timezone.utc)
    
    try:
        for db_config in db_configs:
            print(f"🔍 Processing DB config: {db_config.name or 'unnamed'}")
            
            # Find matching config in API response by name
            matching_api_config = None
            matching_client = None
            
            for api_config in data.get('obj', []):
                api_config_name = api_config.get('remark', '').strip()
                db_config_name = (db_config.name or '').strip()
                
                print(f"🔍 Comparing: '{api_config_name}' vs '{db_config_name}'")
                
                if api_config_name and db_config_name and api_config_name == db_config_name:
                    print(f"✅ Found matching config by name: {api_config_name}")
                    matching_api_config = api_config
                    
                    # Find client with matching tgId
                    import json
                    try:
                        settings = json.loads(api_config.get('settings', '{}'))
                    except Exception:
                        settings = {}
                    
                    clients = settings.get('clients', [])
                    for client in clients:
                        tg_id = client.get('tgId')
                        if str(tg_id) == str(user_code):
                            print(f"✅ Found matching client with tgId: {tg_id}")
                            matching_client = client
                            break
                    break
            
            # Prepare config data
            config_data = {
                'id': db_config.id,
                'name': db_config.name or 'Unnamed Config',
                'vless_url': db_config.vless_url,
                'created_at': db_config.created_at.isoformat(),
                'is_active': db_config.is_active,
                'status': 'active' if db_config.is_active and not db_config.is_expired() else 'inactive',
                'protocol': matching_api_config.get('protocol') if matching_api_config else 'unknown',
                'port': matching_api_config.get('port') if matching_api_config else 0,
                'client_email': matching_client.get('email') if matching_client else 'unknown',
                'client_id': matching_client.get('id') if matching_client else 'unknown',
                'client_enable': matching_client.get('enable') if matching_client else False,
                'client_total_gb': round(matching_client.get('totalGB', 0) / (1024**3), 2) if matching_client else 0,
                'gb_value': round(db_config.total_bytes / (1024**3), 2),
                'used_gb': round(db_config.used_bytes / (1024**3), 2),
                'remaining_gb': round(db_config.get_remaining_bytes() / (1024**3), 2),
                'usage_percentage': round(db_config.get_usage_percentage(), 1),
                'days_remaining': db_config.get_days_remaining(),
                'expiry_time': int(db_config.expires_at.timestamp() * 1000) if db_config.expires_at else None,
            }
            
            # Update usage data from API if available
            if matching_client:
                api_used_bytes = matching_client.get('up', 0) + matching_client.get('down', 0)
                total_gb = matching_client.get('totalGB', 0)
                
                config_data['used_gb'] = round(api_used_bytes / (1024**3), 2)
                config_data['remaining_gb'] = round((total_gb - api_used_bytes) / (1024**3), 2)
                
                # Handle division by zero for unlimited configs (totalGB = 0)
                if total_gb == 0:
                    config_data['usage_percentage'] = 0  # Unlimited configs show 0% usage
                else:
                    config_data['usage_percentage'] = round((api_used_bytes / total_gb) * 100, 1)
            
            combined_configs.append(config_data)
            print(f"✅ Added config: {config_data['name']}")
        
        print(f"✅ Final configs count: {len(combined_configs)}")
        
    except Exception as e:
        print(f"❌ Error processing configs: {e}")
        return JsonResponse({'success': False, 'message': 'Error processing configs'}, status=500)

    return JsonResponse({
        'success': True,
        'configs': combined_configs,
        'message': f'Found {len(combined_configs)} configs'
    })


def report_webapp(request):
    """Report webapp view"""
    user_id = request.GET.get('user_id')
    return render(request, 'orders/report_webapp.html', {'user_id': user_id})


@csrf_exempt
@require_POST
def submit_report(request):
    """Submit a config problem report"""
    try:
        print(f"📋 Report submission request received")
        print(f"📋 Request body: {request.body}")
        
        data = json.loads(request.body)
        telegram_id = data.get('telegram_id')
        problem_description = data.get('problem_description')
        has_tested = data.get('has_tested', False)
        
        print(f"📋 Parsed data - telegram_id: {telegram_id}, problem_description: {problem_description[:50]}..., has_tested: {has_tested}")
        
        if not telegram_id or not problem_description:
            print(f"❌ Missing required data - telegram_id: {telegram_id}, problem_description: {problem_description}")
            return JsonResponse({
                'success': False,
                'message': 'اطلاعات ناقص است'
            })
        
        # Get user
        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if not user:
            print(f"❌ User not found for telegram_id: {telegram_id}")
            return JsonResponse({
                'success': False,
                'message': 'کاربر یافت نشد'
            })
        
        print(f"✅ User found: {user.full_name} (ID: {user.telegram_id})")
        
        # Check if ConfigReport table exists
        try:
            ConfigReport.objects.count()
            print(f"✅ ConfigReport table exists and is accessible")
        except Exception as table_error:
            print(f"❌ ConfigReport table error: {table_error}")
            return JsonResponse({
                'success': False,
                'message': 'خطا در دسترسی به پایگاه داده'
            })
        
        # Create report
        report = ConfigReport.objects.create(
            user=user,
            problem_description=problem_description,
            has_tested=has_tested
        )
        
        print(f"✅ Report created successfully: {report.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'گزارش با موفقیت ارسال شد'
        })
        
    except Exception as e:
        print(f"❌ Error submitting report: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': 'خطا در ارسال گزارش'
        })


@csrf_exempt
@require_GET
def admin_reports_list(request):
    """Get list of reports for admin panel"""
    try:
        # Check if user is admin
        telegram_id = request.GET.get('telegram_id')
        if not telegram_id:
            return JsonResponse({'success': False, 'message': 'شناسه تلگرام مورد نیاز است'})
        
        user = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
        if not user:
            return JsonResponse({'success': False, 'message': 'دسترسی غیرمجاز'})
        
        # Get all reports
        reports = ConfigReport.objects.all().order_by('-created_at')
        reports_data = []
        
        for report in reports:
            reports_data.append({
                'id': report.id,
                'user_name': report.user.full_name,
                'user_code': report.user.user_code,
                'telegram_id': report.user.telegram_id,
                'problem_description': report.problem_description,
                'has_tested': report.has_tested,
                'is_resolved': report.is_resolved,
                'created_at': report.created_at.strftime('%Y/%m/%d %H:%M'),
                'resolved_at': report.resolved_at.strftime('%Y/%m/%d %H:%M') if report.resolved_at else None,
                'resolved_by': report.resolved_by.full_name if report.resolved_by else None
            })
        
        return JsonResponse({
            'success': True,
            'reports': reports_data
        })
        
    except Exception as e:
        print(f"Error getting reports list: {e}")
        return JsonResponse({
            'success': False,
            'message': 'خطا در دریافت گزارشات'
        })


@csrf_exempt
@require_GET
def test_config_report(request):
    """Test endpoint to check if ConfigReport model is working"""
    try:
        # Try to create a test report
        test_user = TelegramUser.objects.first()
        if not test_user:
            return JsonResponse({
                'success': False,
                'message': 'No users found in database'
            })
        
        test_report = ConfigReport.objects.create(
            user=test_user,
            problem_description='Test report',
            has_tested=True
        )
        
        # Delete the test report
        test_report.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'ConfigReport model is working correctly'
        })
        
    except Exception as e:
        print(f"Error testing ConfigReport: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'ConfigReport model error: {str(e)}'
        })


@csrf_exempt
@require_POST
def resolve_report(request):
    """Mark a report as resolved"""
    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        telegram_id = data.get('telegram_id')
        
        if not report_id or not telegram_id:
            return JsonResponse({
                'success': False,
                'message': 'اطلاعات ناقص است'
            })
        
        # Check if user is admin
        admin_user = TelegramUser.objects.filter(telegram_id=telegram_id, role='admin').first()
        if not admin_user:
            return JsonResponse({
                'success': False,
                'message': 'دسترسی غیرمجاز'
            })
        
        # Get report
        report = ConfigReport.objects.filter(id=report_id).first()
        if not report:
            return JsonResponse({
                'success': False,
                'message': 'گزارش یافت نشد'
            })
        
        # Mark as resolved
        report.is_resolved = True
        report.resolved_at = timezone.now()
        report.resolved_by = admin_user
        report.save()
        
        return JsonResponse({
            'success': True,
            'message': 'گزارش حل شد'
        })
        
    except Exception as e:
        print(f"Error resolving report: {e}")
        return JsonResponse({
            'success': False,
            'message': 'خطا در حل گزارش'
        })


