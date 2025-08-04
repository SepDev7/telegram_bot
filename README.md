# 🤖 Telegram Bot with Web App Integration

A Telegram bot with a beautiful Persian web app interface for configuration management.

## 🚀 Quick Start

### **Prerequisites**

1. **Server setup**: Configure your server domain and IP
2. **X-UI Panel**: Make sure x-ui panel is running
3. **Python dependencies**: Install required packages

### **Setup Steps**

1. **Configure Server Settings**

   ```bash
   python setup_server.py
   ```

   Or manually edit `config.py`:

   ```python
   SERVER_DOMAIN = "your-domain.com"
   SERVER_IP = "your-server-ip"
   XUI_PORT = "3030"
   ```

2. **Start Django Server**

   ```bash
   cd cafe_bot_dashboard
   python manage.py runserver
   ```

3. **Start the Bot**
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

1. **Test the web app**: Open your server URL + `/api/config-creator/`
2. **Test the bot**: Send `/start` to your bot
3. **Click "⚙️ ساخت کانفیگ"**: Should open the web app immediately

## 📋 Files Structure

```
telegram/
├── main.py                    # Main bot file
├── config.py                  # Server configuration
├── setup_server.py            # Interactive server setup
├── cafe_bot_dashboard/        # Django project
│   ├── orders/
│   │   ├── models.py         # Database models
│   │   ├── views.py          # Web app views
│   │   ├── urls.py           # URL routing
│   │   └── templates/        # Web app templates
│   └── manage.py
├── requirements.txt           # Python dependencies
├── start_ngrok_bot.bat       # Windows startup script
└── SERVER_SETUP.md           # Detailed setup guide
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

## 🌐 Configuration Options

### **Option 1: Domain + IP (Recommended)**

```python
SERVER_DOMAIN = "yourdomain.com"  # Public domain
SERVER_IP = "192.168.1.100"       # Internal IP
```

### **Option 2: IP Only**

```python
SERVER_DOMAIN = "your-server-ip"  # Same as IP
SERVER_IP = "your-server-ip"      # Server IP
```

### **Option 3: Localhost (Development)**

```python
SERVER_DOMAIN = "localhost"
SERVER_IP = "127.0.0.1"
```

## 🔒 Security Considerations

- ✅ **HTTPS required** for production
- ✅ **Firewall configuration** for x-ui panel
- ✅ **Strong passwords** for x-ui admin
- ✅ **Regular updates** for security patches

## 🚀 Deployment

1. **Production Server**: Use a VPS with domain
2. **SSL Certificate**: Configure HTTPS
3. **Reverse Proxy**: Use nginx/apache
4. **Process Manager**: Use systemd or supervisor

## 📞 Support

- **Documentation**: See `SERVER_SETUP.md`
- **Configuration**: Run `python setup_server.py`
- **Testing**: Use `python test_xui_api.py`
