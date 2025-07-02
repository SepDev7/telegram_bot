import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

API_URL = "http://127.0.0.1:8000/api/create-order/"
BOT_TOKEN = "7752051924:AAGPwvlxTxAKED0T3DpHk8UJ8EONqYBgfJY"

# Static menu (or you can fetch from Django API later)
MENU = {
    1: "Espresso",
    2: "Latte",
    3: "Cappuccino"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, callback_data=str(item_id))]
        for item_id, name in MENU.items()
    ]
    await update.message.reply_text(
        "☕ لطفاً یکی از آیتم‌های منو را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    item_id = int(query.data)
    user = query.from_user

    data = {
        "item": item_id,
        "customer_name": user.full_name,
        "telegram_username": user.username or "",
        "status": "new"
    }

    # Send to Django API
    try:
        res = requests.post(API_URL, json=data)
        if res.status_code == 201:
            await query.edit_message_text(f"✅ سفارش شما برای {MENU[item_id]} ثبت شد.")
        else:
            await query.edit_message_text("❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.")
    except Exception as e:
        await query.edit_message_text("⚠️ خطا در ارتباط با سرور.")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_order))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
