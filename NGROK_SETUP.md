# 🚀 Ngrok Setup for Telegram Bot

## **📋 Prerequisites**

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com)
2. **Sign up for free account**: Get your authtoken
3. **Configure ngrok**: `ngrok config add-authtoken YOUR_TOKEN`

## **🔧 Setup Steps**

### **1. Start Django Server**

```bash
cd cafe_bot_dashboard
python manage.py runserver 127.0.0.1:8000
```

### **2. Start ngrok Tunnel**

```bash
ngrok http 8000
```

### **3. Update Bot Configuration**

Copy the HTTPS URL from ngrok (e.g., `https://abc123.ngrok.io`) and update it in `main.py`:

```python
NGROK_URL = "https://your-ngrok-url.ngrok.io"  # Replace with your ngrok URL
```

### **4. Start the Bot**

```bash
python main.py
```

## **🧪 Testing**

1. **Test the web app**: Open your ngrok URL + `/api/config-creator/`
2. **Test the bot**: Send `/start` to your bot
3. **Click "⚙️ ساخت کانفیگ"**: Should open the web app immediately

## **📱 User Experience**

When users click "⚙️ ساخت کانفیگ":

- ✅ **Opens web app immediately** - no intermediate steps
- ✅ **Beautiful Persian interface** - matches NiceRay Reality
- ✅ **Full functionality** - configuration creation, balance checking
- ✅ **Works with ngrok** - public HTTPS URL

## **🔧 Admin Commands**

```bash
# Verify a user
/verify <user_code>

# Add balance to user
/addbalance <user_code> <amount>

# Make user admin
/makeadmin <user_code>

# Open admin panel
/adminweb
```

## **📋 Files Structure**

```
telegram/
├── main.py                    # Main bot file (updated for ngrok)
├── cafe_bot_dashboard/        # Django project
│   ├── orders/
│   │   ├── models.py         # Database models
│   │   ├── views.py          # Web app views
│   │   ├── urls.py           # URL routing
│   │   └── templates/        # Web app templates
│   └── manage.py
├── requirements.txt           # Python dependencies
└── NGROK_SETUP.md           # This guide
```

## **🎉 Success!**

You now have:

- ✅ **Ngrok tunnel** - public HTTPS URL
- ✅ **Direct web app access** - click button → opens immediately
- ✅ **Beautiful Persian interface** - matches NiceRay Reality
- ✅ **Full functionality** - configuration creation, balance checking
- ✅ **Clean codebase** - removed unnecessary files

**Start testing now!** 🚀
