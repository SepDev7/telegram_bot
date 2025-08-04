# 🚀 Server Setup Guide

This guide explains how to configure your Telegram bot to work with your server instead of ngrok.

## 📋 What Changed

The code has been updated to replace ngrok URLs and localhost references with configurable server settings:

### 🔧 Configuration Changes

1. **Centralized Configuration**: All server settings are now in `config.py`
2. **Server Domain**: Used for public web app URLs and VLESS URLs
3. **Server IP**: Used for internal X-UI API calls
4. **X-UI Settings**: Configurable port, path, username, and password

### 📁 Files Modified

- `main.py` - Updated to use server domain for web app URLs
- `cafe_bot_dashboard/orders/views.py` - Updated X-UI API calls and VLESS URL generation
- `config.py` - New centralized configuration file
- `setup_server.py` - New setup script for easy configuration

## 🛠️ Quick Setup

### 1. Run the Setup Script

```bash
python setup_server.py
```

This interactive script will help you configure:

- Your server domain
- Your server IP address
- X-UI panel settings
- Bot token

### 2. Manual Configuration

If you prefer to configure manually, edit `config.py`:

```python
# Your server domain (for public access)
SERVER_DOMAIN = "yourdomain.com"

# Your server IP address (for internal API calls)
SERVER_IP = "192.168.1.100"

# X-UI Panel Configuration
XUI_PORT = "3030"
XUI_PATH = "RZElYrcIBosloBn"
XUI_USERNAME = "admin"
XUI_PASSWORD = "admin"
```

## 🌐 URL Structure

### Before (ngrok):

- Web apps: `https://abc123.ngrok-free.app/api/config-creator/`
- X-UI API: `https://abc123.ngrok-free.app/RZElYrcIBosloBn/login`
- VLESS URLs: `vless://...@guard.stormserver.eu:port`

### After (your server):

- Web apps: `https://yourdomain.com/api/config-creator/`
- X-UI API: `http://your-server-ip:3030/RZElYrcIBosloBn/login`
- VLESS URLs: `vless://...@yourdomain.com:port`

## 🔧 Configuration Options

### Option 1: Domain + IP

```python
SERVER_DOMAIN = "yourdomain.com"  # For public access
SERVER_IP = "192.168.1.100"       # For internal API calls
```

### Option 2: IP Only

```python
SERVER_DOMAIN = "your-server-ip"  # Use IP for both
SERVER_IP = "your-server-ip"      # Same IP for internal calls
```

### Option 3: Localhost (Development)

```python
SERVER_DOMAIN = "localhost"
SERVER_IP = "127.0.0.1"
```

## 🔒 Security Considerations

1. **X-UI Panel**: Make sure it's not publicly accessible
2. **Firewall**: Only allow access to X-UI port from your application
3. **HTTPS**: Use HTTPS for public web app URLs
4. **Credentials**: Store X-UI credentials securely

## 🧪 Testing Your Configuration

### 1. Validate Configuration

```bash
python setup_server.py validate
```

### 2. Test X-UI Connection

```bash
python test_xui_api.py
```

### 3. Test Web App URLs

Visit: `https://yourdomain.com/api/config-creator/`

## 📝 Environment-Specific Setup

### Development Environment

```python
SERVER_DOMAIN = "localhost"
SERVER_IP = "127.0.0.1"
BASE_URL = "http://localhost:8000"  # Django development server
```

### Production Environment

```python
SERVER_DOMAIN = "yourdomain.com"
SERVER_IP = "your-server-ip"
BASE_URL = "https://yourdomain.com"  # HTTPS for production
```

## 🚨 Troubleshooting

### Common Issues

1. **X-UI Connection Failed**

   - Check if X-UI is running on the correct port
   - Verify firewall settings
   - Test with: `curl http://your-server-ip:3030`

2. **Web App Not Accessible**

   - Check DNS configuration
   - Verify HTTPS certificate
   - Test with: `curl https://yourdomain.com`

3. **VLESS URLs Not Working**
   - Ensure SERVER_DOMAIN is correct
   - Check if the domain resolves to your server
   - Verify port forwarding

### Debug Commands

```bash
# Test X-UI connectivity
curl -X POST http://your-server-ip:3030/RZElYrcIBosloBn/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Test web app accessibility
curl https://yourdomain.com/api/config-creator/

# Check DNS resolution
nslookup yourdomain.com
```

## 📚 Additional Resources

- [X-UI Documentation](https://github.com/vaxilu/x-ui)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [SSL Certificate Setup](https://letsencrypt.org/)

## 🔄 Migration Checklist

- [ ] Update `config.py` with your server details
- [ ] Test X-UI API connectivity
- [ ] Verify web app accessibility
- [ ] Test VLESS URL generation
- [ ] Update DNS records (if using domain)
- [ ] Configure firewall rules
- [ ] Set up HTTPS certificate
- [ ] Test bot functionality

## 💡 Tips

1. **Start with IP only** for testing, then add domain later
2. **Use environment variables** for sensitive data in production
3. **Monitor logs** for connection issues
4. **Backup your configuration** before making changes
5. **Test thoroughly** before deploying to production
