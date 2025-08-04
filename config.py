# Server Configuration
# Replace these values with your actual server information

# Your server domain (for public access)
SERVER_DOMAIN = "guard.stormserver.eu"  # Replace with your actual domain

# Your server IP address (for internal API calls)
SERVER_IP = "91.107.162.165"  # Replace with your actual server IP

# X-UI Panel Configuration
XUI_PORT = "3030"  # X-UI panel port
XUI_PATH = "RZElYrcIBosloBn"  # X-UI panel path
XUI_USERNAME = "admin"  # X-UI username
XUI_PASSWORD = "admin"  # X-UI password

# Construct URLs
BASE_URL = f"https://{SERVER_DOMAIN}"  # For web apps and public access
XUI_BASE_URL = f"http://{SERVER_IP}:{XUI_PORT}"  # For internal X-UI API calls

# Bot Configuration
BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"

# Django Configuration
DJANGO_SETTINGS_MODULE = "cafe_bot_dashboard.settings"

# Example configuration for different environments:
# 
# Development (localhost):
# SERVER_DOMAIN = "localhost"
# SERVER_IP = "127.0.0.1"
# 
# Production (with domain):
# SERVER_DOMAIN = "yourdomain.com"
# SERVER_IP = "192.168.1.100"
# 
# Production (with IP only):
# SERVER_DOMAIN = "your-server-ip"
# SERVER_IP = "your-server-ip" 