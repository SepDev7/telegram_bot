# 🤖 Telegram Bot with Web App Integration

A Telegram bot with a beautiful Persian web app interface for configuration management.

## 🚀 Quick Start

### **Prerequisites**

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com)
2. **Sign up for free account**: Get your authtoken
3. **Configure ngrok**: `ngrok config add-authtoken YOUR_TOKEN`

### **Setup Steps**

1. **Start Django Server**

   ```bash
   cd cafe_bot_dashboard
   python manage.py runserver 127.0.0.1:8000
   ```

2. **Start ngrok Tunnel**

   ```bash
   ngrok http 8000
   ```

3. **Update Bot Configuration**
   Copy the HTTPS URL from ngrok and update it in `main.py`:

   ```python
   NGROK_URL = "https://your-ngrok-url.ngrok.io"  # Replace with your ngrok URL
   ```

4. **Start the Bot**
   ```bash
   python main.py
   ```

## 📱 Features

### **User Panel**

- ✅ **Detailed user statistics** - active/inactive configs, balance
- ✅ **Beautiful Persian interface** - RTL design
- ✅ **Navigation buttons** - wallet, configs, settings, reports

### **Web App Integration**

- ✅ **Direct web app access** - click button → opens immediately
- ✅ **Beautiful Persian interface** - matches NiceRay Reality
- ✅ **Full functionality** - configuration creation, balance checking
- ✅ **Form validation** - client and server-side validation

### **Admin Features**

- ✅ **User verification** - `/verify <user_code>`
- ✅ **Balance management** - `/addbalance <user_code> <amount>`
- ✅ **Admin panel** - `/adminweb`
- ✅ **Role management** - `/makeadmin <user_code>`

## 🧪 Testing

1. **Test the web app**: Open your ngrok URL + `/api/config-creator/`
2. **Test the bot**: Send `/start` to your bot
3. **Click "⚙️ ساخت کانفیگ"**: Should open the web app immediately

## 📋 Files Structure

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
├── start_ngrok_bot.bat       # Windows startup script
└── NGROK_SETUP.md           # Detailed setup guide
```

## 🔧 Admin Commands

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

## 🎉 User Experience

When users click "⚙️ ساخت کانفیگ":

- ✅ **Opens web app immediately** - no intermediate steps
- ✅ **Beautiful Persian interface** - matches NiceRay Reality
- ✅ **Full functionality** - configuration creation, balance checking
- ✅ **Works with ngrok** - public HTTPS URL

## 📚 Documentation

- **NGROK_SETUP.md** - Detailed ngrok setup guide
- **start_ngrok_bot.bat** - Windows one-click startup

## 🚀 Success!

You now have:

- ✅ **Ngrok tunnel** - public HTTPS URL
- ✅ **Direct web app access** - click button → opens immediately
- ✅ **Beautiful Persian interface** - matches NiceRay Reality
- ✅ **Full functionality** - configuration creation, balance checking
- ✅ **Clean codebase** - removed unnecessary files

**Start testing now!** 🚀
