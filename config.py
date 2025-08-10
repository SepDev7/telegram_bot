# Server Configuration
# Replace these values with your actual server information

# Your server domain (for public access)
SERVER_DOMAIN = "testbot.stormserver.eu"  # Replace with your actual domain

# Your server IP address (for internal API calls)
# SERVER_IP = "91.107.162.165"  # Replace with your actual server IP

# X-UI Panel Configuration
XUI_PORT = "2096"  # X-UI panel port
XUI_PATH = "bot"  # X-UI panel path
XUI_USERNAME = "admin"  # X-UI username
XUI_PASSWORD = "Reza3830063"  # X-UI password

# Construct URLs
BASE_URL = f"https://{SERVER_DOMAIN}"  # For web apps and public access
XUI_BASE_URL = f"https://{SERVER_DOMAIN}:{XUI_PORT}"  # For internal X-UI API calls

# Bot Configuration
BOT_TOKEN = "8098610006:AAEMg2WcrE0DexwQ1wt9Fv72Qa5zEBF8lN0"

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