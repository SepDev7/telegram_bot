import asyncio
import json
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, ApplicationBuilder

# Your bot token - replace with your actual token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def test_webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple test handler for web app data"""
    print("🔍 Test webapp handler called!")
    print(f"🔍 Update: {update}")
    print(f"🔍 Message: {update.message}")
    
    if update.message and update.message.web_app_data:
        print(f"🔍 Web app data found: {update.message.web_app_data.data}")
        try:
            data = json.loads(update.message.web_app_data.data)
            print(f"🔍 Parsed data: {data}")
            
            # Send a simple response
            await update.message.reply_text("✅ Web app data received successfully!")
            
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
            await update.message.reply_text("❌ Error parsing web app data")
    else:
        print("❌ No web app data found")
        await update.message.reply_text("❌ No web app data received")

async def main():
    """Main function to test the bot"""
    print("🔍 Starting test bot...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add the test handler
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, test_webapp_handler))
    
    print("🔍 Bot started. Press Ctrl+C to stop.")
    
    try:
        await app.run_polling()
    except KeyboardInterrupt:
        print("🔍 Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main()) 