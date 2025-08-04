# 🚫 DEPRECATED: Ngrok Setup for Telegram Bot

> **⚠️ This guide is deprecated. The bot now uses server-based configuration instead of ngrok.**

## **📋 Migration Required**

The bot has been updated to use server-based configuration instead of ngrok. Please use the new setup:

### **New Setup Guide**

1. **Use the new configuration**: See `SERVER_SETUP.md`
2. **Run setup script**: `python setup_server.py`
3. **Configure your server**: Edit `config.py`

### **Why the Change?**

- ✅ **More stable** - No dependency on ngrok service
- ✅ **Better performance** - Direct server access
- ✅ **More secure** - Full control over your infrastructure
- ✅ **Production ready** - Suitable for production deployment

## **🚀 Quick Migration**

1. **Run the setup script**:

   ```bash
   python setup_server.py
   ```

2. **Configure your server details**:

   ```python
   # In config.py
   SERVER_DOMAIN = "your-domain.com"
   SERVER_IP = "your-server-ip"
   XUI_PORT = "3030"
   ```

3. **Start the bot**:
   ```bash
   python main.py
   ```

## **📚 New Documentation**

- **SERVER_SETUP.md** - Complete server setup guide
- **README.md** - Updated main documentation
- **config.py** - Centralized configuration

## **🔧 Support**

If you need help migrating:

1. Read `SERVER_SETUP.md`
2. Run `python setup_server.py`
3. Check `README.md` for updated instructions

---

**This ngrok setup guide is no longer maintained. Please use the new server-based configuration.**
