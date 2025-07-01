from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

MENU = {
    "Coffee": 50000,
    "Latte": 60000,
    "Espresso": 45000
}

ADMIN_ID = 123456789  # Replace with your Telegram ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to our cafe bot! Type /menu to see the drinks.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(f"{item} - {price}T", callback_data=item)]
        for item, price in MENU.items()
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Choose an item to order:", reply_markup=reply_markup)

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item = query.data
    user = query.from_user
    message = f"{user.full_name} ordered: {item}"
    data = {
        "item": get_menu_item_id(item),
        "customer_name": user.full_name,
        "telegram_username": user.username or "",
        "status": "new"
    }
    
    await query.answer("Order received!")
    await query.edit_message_text(text=f"✅ You ordered: {item}")
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    
    requests.post("https://yourdomain.com/api/create-order/", json=data)

if __name__ == "__main__":
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(handle_order))

    app.run_polling()
