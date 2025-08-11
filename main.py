import os
import sys
import django

# Add the Django project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cafe_bot_dashboard'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_bot_dashboard.settings')

# Configure Django
django.setup()

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, CallbackContext, MessageHandler, filters
)
import functools
from asgiref.sync import sync_to_async
from orders.models import TelegramUser, Configuration, VlessConfig
from telegram.constants import ParseMode
import datetime

# Import configuration
from config import BOT_TOKEN, BASE_URL

# For webapp URLs, we'll use HTTPS domain (Telegram requires HTTPS)
WEBAPP_BASE_URL = f"https://guard.stormserver.eu"

# Replace with dynamic fetching later if needed
MENU = {
    1: "Espresso",
    2: "Latte",
    3: "Cappuccino"
}

# In-memory cart per user (you may want to persist it later)
user_carts = {}

# Global bot application instance for notifications
bot_app = None

async def send_notification_to_admins(message: str):
    """Send notification to all admin users"""
    global bot_app
    if not bot_app:
        return
    
    try:
        # Get all admin users
        get_admins = sync_to_async(TelegramUser.objects.filter(role='admin').values_list('telegram_id', flat=True))
        admin_ids = await get_admins()
        
        for admin_id in admin_ids:
            try:
                await bot_app.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                print(f"❌ Failed to send notification to admin {admin_id}: {e}")
    except Exception as e:
        print(f"❌ Error sending admin notifications: {e}")

async def send_notification_to_user(telegram_id: int, message: str):
    """Send notification to a specific user"""
    global bot_app
    if not bot_app:
        return
    
    try:
        await bot_app.bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"❌ Failed to send notification to user {telegram_id}: {e}")

async def send_menu_to_user(telegram_id: int):
    """Send the main menu to a user after verification"""
    global bot_app
    if not bot_app:
        return
    
    try:
        # Get user info
        get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=telegram_id).first)
        user = await get_user()
        
        if not user:
            return
        
        # Create main menu keyboard
        keyboard = [
            [InlineKeyboardButton("🛒 منو", callback_data="menu")],
            [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
            [InlineKeyboardButton("📋 گزارش", callback_data="report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot_app.bot.send_message(
            chat_id=telegram_id,
            text="🎉 <b>تبریک! حساب کاربری شما تایید شد!</b>\n\nحالا می‌توانید از تمام امکانات ربات استفاده کنید:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"❌ Failed to send menu to user {telegram_id}: {e}")

def only_verified(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
        try:
            # Direct database check instead of API
            get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id).first)
            user = await get_user()
            if not user or not user.is_verified:
                await (update.message or update.callback_query).reply_text(
                    "⏳ منتظر تایید مدیر بمانید تا بتوانید از ربات استفاده کنید."
                )
                return
        except Exception as e:
            print("❌ Error in only_verified:", e)
            await (update.message or update.callback_query).reply_text(
                "⚠️ مشکلی پیش آمده. لطفاً بعداً امتحان کنید."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    username = update.effective_user.username or ""

    try:
        # Check if user already exists
        get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id).first)
        user = await get_user()
        
        if user:
            # User exists
            if user.is_verified:
                # Show the user panel for verified users
                await show_user_panel(update, user)
            else:
                await update.message.reply_text(
                    f"👋 سلام {full_name}!\n"
                    f"کد کاربری شما: `{user.user_code}`\n\n"
                    "⏳ منتظر تایید مدیر بمانید تا بتوانید از ربات استفاده کنید."
                )
        else:
            # Create new user
            create_user = sync_to_async(TelegramUser.objects.create)
            user = await create_user(
                telegram_id=user_id,
                full_name=full_name,
                telegram_username=username,
            )
            await update.message.reply_text(
                f"👋 سلام {full_name}!\n"
                f"ثبت‌نام شما با موفقیت انجام شد.\n"
                f"کد کاربری شما: `{user.user_code}`\n\n"
                "✅ لطفاً منتظر تایید مدیر بمانید تا بتوانید از ربات استفاده کنید."
            )
            
            # Send notification to admins about new user
            admin_message = f"👤 <b>کاربر جدید ثبت‌نام کرد!</b>\n\n" \
                           f"📝 نام: {full_name}\n" \
                           f"🆔 کد کاربری: <code>{user.user_code}</code>\n" \
                           f"👤 یوزرنیم: @{username if username else 'بدون یوزرنیم'}\n\n" \
                           f"برای تایید کاربر از دستور زیر استفاده کنید:\n" \
                           f"<code>/verify {user.user_code}</code>"
            
            await send_notification_to_admins(admin_message)
    except Exception as e:
        print("❌ Error in /start:", e)
        await update.message.reply_text("⚠️ مشکلی پیش آمده. لطفاً بعداً امتحان کنید.")

async def show_user_panel(update: Update, user: TelegramUser):
    """Display the main user panel with statistics and navigation buttons"""
    
    # Get user statistics
    get_active_configs = sync_to_async(VlessConfig.objects.filter(user=user, is_active=True).count)
    get_inactive_configs = sync_to_async(VlessConfig.objects.filter(user=user, is_active=False).count)
    
    active_configs = await get_active_configs()
    inactive_configs = await get_inactive_configs()
    
    # Create panel message
    panel_text = (
        f"#️⃣ کد پنل : {user.user_code}\n"
        f"👤 پنل کاربری : «{user.full_name}»\n"
        f"✅ کانفیگ های فعال : {active_configs}\n"
        f"⭐ کانفیگ های غیر فعال : {inactive_configs}\n"
        f"💰 موجودی من : {user.balance} سکه\n\n"
        f"💎 از طریق دکمه های زیر میتوانید به بخشهای مختلف ربات دسترسی داشته باشید.\n\n"
        f"v3.9.1 {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    
    # Create navigation buttons
    rules_url = f"{WEBAPP_BASE_URL}/api/rules/?user_id={user.telegram_id}"
    keyboard = [
        [
            InlineKeyboardButton("⚙️ ساخت کانفیگ", callback_data="create_config"),
            InlineKeyboardButton("💼 کیف پول", callback_data="wallet")
        ],
        [
            InlineKeyboardButton("کانفیگ ها", callback_data="my_configs"),
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_panel")
        ],
        [
            InlineKeyboardButton("📢 کانال", callback_data="channel"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")
        ],
        [
            InlineKeyboardButton("📋 گزارش", callback_data="report"),
            InlineKeyboardButton("📜 قوانین", web_app=WebAppInfo(url=rules_url))
        ]
    ]
    
    # Add admin panel button for admin users
    if user.role == 'admin':
        admin_webapp_url = f"{WEBAPP_BASE_URL}/api/admin-webapp/?user_id={user.telegram_id}"
        keyboard.append([InlineKeyboardButton("🛠️ پنل مدیریت", web_app=WebAppInfo(url=admin_webapp_url))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(panel_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(panel_text, reply_markup=reply_markup)

async def handle_panel_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all panel button actions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id).first)
    user = await get_user()
    
    if query.data == "create_config":
        await show_create_config_panel(query, user)
    elif query.data == "wallet":
        await show_wallet_panel(query, user)
    elif query.data == "my_configs":
        await show_my_configs_panel(query, user)
    elif query.data == "refresh_panel":
        await show_user_panel(update, user)
    elif query.data == "channel":
        await show_channel_panel(query)
    elif query.data == "settings":
        await show_settings_panel(query, user)
    elif query.data == "report":
        await show_report_panel(query)


    elif query.data == "rules":
        await show_rules_panel(query)
    elif query.data == "back_to_main":
        await show_user_panel(update, user)
    elif query.data == "add_balance":
        await show_add_balance_panel(query, user)
    elif query.data == "transaction_history":
        await show_transaction_history(query, user)
    elif query.data == "manage_configs":
        await show_manage_configs_panel(query, user)
    elif query.data == "change_name":
        await show_change_name_panel(query, user)
    elif query.data == "notification_settings":
        await show_notification_settings(query, user)
    elif query.data == "usage_stats":
        await show_usage_stats(query, user)
    elif query.data == "financial_report":
        await show_financial_report(query, user)
    elif query.data == "online_payment":
        await show_online_payment_panel(query, user)
    elif query.data.startswith("toggle_config_"):
        config_id = int(query.data.replace("toggle_config_", ""))
        await toggle_config_status(query, user, config_id)

async def show_create_config_panel(query, user):
    """Show configuration creation options"""
    
    # Use Django server URL for web app
    webapp_url = f"{WEBAPP_BASE_URL}/api/config-creator/?user_id={user.telegram_id}"
    keyboard = [
        [InlineKeyboardButton("⚙️ ساخت کانفیگ", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    text = (
        f"⚙️ ساخت کانفیگ جدید\n\n"
        f"برای ساخت کانفیگ جدید، روی دکمه زیر کلیک کنید تا پنل پیشرفته باز شود.\n\n"
        f"💰 موجودی شما: {user.balance} سکه"
    )
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))



async def show_wallet_panel(query, user):
    """Show wallet panel with settlement instructions and webapp button"""
    text = (
        "✅ جهت تسویه حساب مبلغ مورد نظر را به شماره کارت زیر واریز کنید:\n"
        "\n"
        "<code>0000-0000-0000-0000</code>\n"
        "\n"
        "👤 بنام: بنده خدا\n"
        "\n"
        "👇 سپس عکس رسید و مبلغ واریزی را از طریق دکمه \"ارسال رسید\" ارسال کنید و منتظر تایید باشید\n"
        "بعد از تایید، اطلاعیه از طریق ربات به شما ارسال خواهد شد."
    )
    webapp_url = f"{WEBAPP_BASE_URL}/api/settlement/?user_id={user.telegram_id}"
    wallet2wallet_url = f"{WEBAPP_BASE_URL}/api/wallet-to-wallet/?user_id={user.telegram_id}"
    keyboard = [
        [InlineKeyboardButton("ارسال رسید", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("کیف به کیف", web_app=WebAppInfo(url=wallet2wallet_url))],
        [InlineKeyboardButton("بازگشت به پنل کاربری ⬅️", callback_data="back_to_main")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def show_my_configs_panel(query, user):
    """Show user's configurations list web app"""
    
    # Use Django server URL for web app
    webapp_url = f"{WEBAPP_BASE_URL}/api/configs-list/?user_id={user.telegram_id}"
    keyboard = [
        [InlineKeyboardButton("کانفیگ های شما", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    text = (
        f"کانفیگ های شما\n\n"
        f"برای مشاهده و مدیریت کانفیگ‌های خود، روی دکمه زیر کلیک کنید.\n\n"
        f"💰 موجودی شما: {user.balance} سکه"
    )
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_channel_panel(query):
    """Show channel information"""
    text = (
        "📢 کانال رسمی ربات\n\n"
        "برای دریافت آخرین اخبار و به‌روزرسانی‌ها، به کانال ما بپیوندید:\n\n"
        "🔗 @YourBotChannel"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔗 عضویت در کانال", url="https://t.me/YourBotChannel")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_settings_panel(query, user):
    """Show settings web app"""
    
    # Use Django server URL for web app
    webapp_url = f"{WEBAPP_BASE_URL}/api/settings/?user_id={user.telegram_id}"
    keyboard = [
        [InlineKeyboardButton("⚙️ تنظیمات", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    text = (
        f"⚙️ تنظیمات کاربری\n\n"
        f"برای مدیریت تنظیمات خود، روی دکمه زیر کلیک کنید.\n\n"
        f"💰 موجودی شما: {user.balance} سکه"
    )
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_report_panel(query):
    """Show report panel with webapp"""
    text = (
        "📋 گزارش مشکل\n\n"
        "اگر مشکلی با کانفیگ خود دارید، لطفاً آن را گزارش دهید تا پشتیبانی در اسرع وقت به آن رسیدگی کند."
    )
    
    # Get user for webapp URL
    user_id = query.from_user.id
    webapp_url = f"{WEBAPP_BASE_URL}/api/report/?user_id={user_id}"
    
    keyboard = [
        [InlineKeyboardButton("📝 ارسال گزارش", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_rules_panel(query):
    """Show rules panel"""
    text = (
        "📜 قوانین استفاده از ربات\n\n"
        "1️⃣ استفاده از ربات فقط برای اهداف قانونی مجاز است\n"
        "2️⃣ هرگونه سوء استفاده منجر به مسدودیت خواهد شد\n"
        "3️⃣ مسئولیت استفاده از کانفیگ‌ها بر عهده کاربر است\n"
        "4️⃣ ربات حق تغییر قوانین را محفوظ می‌دارد\n\n"
        "با استفاده از ربات، شما این قوانین را پذیرفته‌اید."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_admin_panel(query, user):
    """Show admin panel for admin users"""
    if user.role != 'admin':
        await query.edit_message_text("❌ شما مجاز به دسترسی به پنل مدیریت نیستید.")
        return
    
    webapp_url = f"{WEBAPP_BASE_URL}/api/admin-webapp/?user_id={user.telegram_id}"
    keyboard = [
        [InlineKeyboardButton("🛠️ پنل مدیریت", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        "🛠️ <b>پنل مدیریت</b>\n\n"
        "برای ورود به پنل مدیریت روی دکمه زیر کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

@only_verified
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"add_{item_id}")]
        for item_id, name in MENU.items()
    ]
    await update.message.reply_text(
        "📋 منوی امروز:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@only_verified
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("add_"):
        item_id = int(query.data.replace("add_", ""))
        user_id = query.from_user.id

        cart = user_carts.get(user_id, [])
        cart.append(item_id)
        user_carts[user_id] = cart

        await query.edit_message_text(f"✅ {MENU[item_id]} به سبد خرید اضافه شد.")

@only_verified
async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await update.message.reply_text("🛒 سبد خرید شما خالی است.")
        return

    text = "🛒 سبد خرید شما:\n"
    buttons = []
    for idx, item_id in enumerate(cart):
        text += f"{idx+1}. {MENU[item_id]}\n"
        buttons.append([
            InlineKeyboardButton(f"❌ حذف {MENU[item_id]}", callback_data=f"remove_{idx}")
        ])

    buttons.append([InlineKeyboardButton("✅ تایید و پرداخت", callback_data="confirm")])
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_cart_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("remove_"):
        index = int(query.data.replace("remove_", ""))
        cart = user_carts.get(user_id, [])
        if 0 <= index < len(cart):
            removed = MENU[cart.pop(index)]
            user_carts[user_id] = cart
            await query.edit_message_text(f"❌ {removed} از سبد حذف شد.")
        else:
            await query.edit_message_text("⚠️ آیتم پیدا نشد.")

    elif query.data == "confirm":
        cart = user_carts.get(user_id, [])
        if not cart:
            await query.edit_message_text("🛒 سبد خرید شما خالی است.")
            return

        for item_id in cart:
            data = {
                "item": item_id,
                "customer_name": query.from_user.full_name,
                "telegram_username": query.from_user.username or "",
                "status": "new"
            }
            try:
                res = requests.post(f"{BASE_URL}/api/create-order/", json=data)
                if res.status_code != 201:
                    print("❌ Failed to create order:", res.json())
            except Exception as e:
                print("❌ Error sending request:", e)

        user_carts[user_id] = []
        await query.edit_message_text("✅ سفارش شما ثبت شد. منتظر آماده‌سازی باشید.")

async def adminweb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id).first)
    user = await get_user()
    if not user or user.role != 'admin':
        await update.message.reply_text("❌ You are not authorized to access the admin panel.")
        return
    webapp_url = f"{WEBAPP_BASE_URL}/api/admin-webapp/?user_id={user_id}"
    keyboard = [
        [InlineKeyboardButton("پنل مدیریت", web_app=WebAppInfo(url=webapp_url))]
    ]
    await update.message.reply_text(
        "🛠️ برای ورود به پنل مدیریت روی دکمه زیر کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to verify a user"""
    user_id = update.effective_user.id
    get_admin = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id, role='admin').first)
    admin = await get_admin()
    
    if not admin:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a user code: /verify <user_code>")
        return
    
    try:
        user_code = int(context.args[0])
        get_user = sync_to_async(TelegramUser.objects.filter(user_code=user_code).first)
        user = await get_user()
        
        if not user:
            await update.message.reply_text(f"❌ User with code {user_code} not found.")
            return
        
        if user.is_verified:
            await update.message.reply_text(f"✅ User {user.full_name} is already verified.")
            return
        
        # Verify the user
        update_user = sync_to_async(lambda: TelegramUser.objects.filter(user_code=user_code).update(is_verified=True))
        await update_user()
        
        await update.message.reply_text(f"✅ User {user.full_name} has been verified successfully!")
        
        # Send notification to the user that they are verified
        user_notification = f"🎉 <b>تبریک!</b>\n\nحساب کاربری شما توسط مدیر تایید شد!\n\nکد کاربری: <code>{user.user_code}</code>\n\nحالا می‌توانید از تمام امکانات ربات استفاده کنید."
        await send_notification_to_user(user.telegram_id, user_notification)
        
        # Send the main menu to the user
        await send_menu_to_user(user.telegram_id)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user code. Please provide a valid number.")

async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add balance to a user"""
    user_id = update.effective_user.id
    get_admin = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id, role='admin').first)
    admin = await get_admin()
    
    if not admin:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Please provide user code and amount: /addbalance <user_code> <amount>")
        return
    
    try:
        user_code = int(context.args[0])
        amount = int(context.args[1])
        
        get_user = sync_to_async(TelegramUser.objects.filter(user_code=user_code).first)
        user = await get_user()
        
        if not user:
            await update.message.reply_text(f"❌ User with code {user_code} not found.")
            return
        
        # Add balance
        new_balance = user.balance + amount
        update_user = sync_to_async(lambda: TelegramUser.objects.filter(user_code=user_code).update(balance=new_balance))
        await update_user()
        
        await update.message.reply_text(f"✅ Added {amount} coins to {user.full_name}. New balance: {new_balance} coins")
        
        # Send notification to the user about balance addition
        balance_notification = f"💰 <b>موجودی شما افزایش یافت!</b>\n\n" \
                              f"مبلغ اضافه شده: <code>{amount}</code> سکه\n" \
                              f"موجودی جدید: <code>{new_balance}</code> سکه\n\n" \
                              f"حالا می‌توانید کانفیگ جدید خریداری کنید!"
        await send_notification_to_user(user.telegram_id, balance_notification)

    except ValueError:
        await update.message.reply_text("❌ Invalid input. Please provide valid numbers.")

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to make a user admin"""
    user_id = update.effective_user.id
    get_admin = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id, role='admin').first)
    admin = await get_admin()
    
    if not admin:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a user code: /makeadmin <user_code>")
        return
    
    try:
        user_code = int(context.args[0])
        get_user = sync_to_async(TelegramUser.objects.filter(user_code=user_code).first)
        user = await get_user()
        
        if not user:
            await update.message.reply_text(f"❌ User with code {user_code} not found.")
            return
        
        if user.role == 'admin':
            await update.message.reply_text(f"✅ User {user.full_name} is already an admin.")
            return
        
        # Make user admin
        update_user = sync_to_async(lambda: TelegramUser.objects.filter(user_code=user_code).update(role='admin'))
        await update_user()
        
        await update.message.reply_text(f"✅ User {user.full_name} has been made admin successfully!")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user code. Please provide a valid number.")

async def show_add_balance_panel(query, user):
    """Show add balance panel"""
    text = (
        f"➕ افزایش موجودی\n\n"
        f"💰 موجودی فعلی: {user.balance} سکه\n\n"
        f"برای افزایش موجودی، لطفاً با پشتیبانی تماس بگیرید:\n"
        f"📞 @SupportUsername\n\n"
        f"یا از طریق درگاه پرداخت زیر اقدام کنید:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💳 پرداخت آنلاین", callback_data="online_payment")],
        [InlineKeyboardButton("📞 تماس با پشتیبانی", url="https://t.me/SupportUsername")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="wallet")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_transaction_history(query, user):
    """Show transaction history"""
    text = (
        f"📊 تاریخچه تراکنشات\n\n"
        f"💰 موجودی فعلی: {user.balance} سکه\n\n"
        f"آخرین تراکنشات:\n"
        f"📅 {datetime.datetime.now().strftime('%Y/%m/%d')} - موجودی اولیه\n"
        f"📅 {datetime.datetime.now().strftime('%Y/%m/%d')} - ثبت‌نام\n\n"
        f"برای مشاهده جزئیات بیشتر، با پشتیبانی تماس بگیرید."
    )
    
    keyboard = [
        [InlineKeyboardButton("📞 تماس با پشتیبانی", url="https://t.me/SupportUsername")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="wallet")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_manage_configs_panel(query, user):
    """Show configuration management panel"""
    get_configs = sync_to_async(Configuration.objects.filter(user=user).all)
    configs = await get_configs()
    
    if not configs:
        text = "📋 شما هنوز هیچ کانفیگی ندارید."
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="my_configs")]]
    else:
        text = "🔧 مدیریت کانفیگ‌ها\n\n"
        keyboard = []
        
        for i, config in enumerate(configs):
            status = "✅ فعال" if config.is_active else "❌ غیرفعال"
            text += f"{i+1}. {config.name} - {status}\n"
            keyboard.append([
                InlineKeyboardButton(f"🔄 {config.name}", callback_data=f"toggle_config_{config.id}")
            ])
        
        text += "\nبرای تغییر وضعیت کانفیگ‌ها، روی دکمه مربوطه کلیک کنید."
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="my_configs")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_change_name_panel(query, user):
    """Show change name panel"""
    text = (
        f"📝 تغییر نام\n\n"
        f"نام فعلی: {user.full_name}\n\n"
        f"برای تغییر نام، لطفاً نام جدید خود را ارسال کنید.\n"
        f"یا برای بازگشت، روی دکمه زیر کلیک کنید."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="settings")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_notification_settings(query, user):
    """Show notification settings"""
    text = (
        f"🔔 تنظیمات اعلان\n\n"
        f"تنظیمات فعلی:\n"
        f"✅ اعلان‌های عمومی: فعال\n"
        f"✅ اعلان‌های کانفیگ: فعال\n"
        f"✅ اعلان‌های مالی: فعال\n\n"
        f"برای تغییر تنظیمات، با پشتیبانی تماس بگیرید."
    )
    
    keyboard = [
        [InlineKeyboardButton("📞 تماس با پشتیبانی", url="https://t.me/SupportUsername")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="settings")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_usage_stats(query, user):
    """Show usage statistics"""
    get_configs = sync_to_async(Configuration.objects.filter(user=user).all)
    configs = await get_configs()
    
    active_configs = len([c for c in configs if c.is_active])
    total_configs = len(configs)
    
    text = (
        f"📈 آمار استفاده\n\n"
        f"📊 آمار کلی:\n"
        f"🔧 کل کانفیگ‌ها: {total_configs}\n"
        f"✅ کانفیگ‌های فعال: {active_configs}\n"
        f"❌ کانفیگ‌های غیرفعال: {total_configs - active_configs}\n"
        f"💰 موجودی: {user.balance} سکه\n\n"
        f"📅 تاریخ عضویت: {user.created_at.strftime('%Y/%m/%d') if hasattr(user, 'created_at') else 'نامشخص'}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="report")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_financial_report(query, user):
    """Show financial report"""
    text = (
        f"💰 گزارش مالی\n\n"
        f"💰 موجودی فعلی: {user.balance} سکه\n"
        f"💳 کل تراکنشات: 0\n"
        f"📈 درآمد کل: 0 سکه\n"
        f"📉 هزینه کل: 0 سکه\n\n"
        f"📊 آمار ماهانه:\n"
        f"📅 {datetime.datetime.now().strftime('%B %Y')}: {user.balance} سکه"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="report")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_online_payment_panel(query, user):
    """Show online payment panel"""
    text = (
        f"💳 پرداخت آنلاین\n\n"
        f"💰 موجودی فعلی: {user.balance} سکه\n\n"
        f"مقادیر قابل پرداخت:\n"
        f"💎 100 سکه - 10,000 تومان\n"
        f"💎 500 سکه - 45,000 تومان\n"
        f"💎 1000 سکه - 80,000 تومان\n\n"
        f"برای پرداخت، لطفاً با پشتیبانی تماس بگیرید."
    )
    
    keyboard = [
        [InlineKeyboardButton("📞 تماس با پشتیبانی", url="https://t.me/SupportUsername")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="add_balance")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def toggle_config_status(query, user, config_id):
    """Toggle configuration active/inactive status"""
    try:
        get_config = sync_to_async(Configuration.objects.filter(id=config_id, user=user).first)
        config = await get_config()
        
        if not config:
            await query.edit_message_text(
                "❌ کانفیگ مورد نظر یافت نشد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="manage_configs")]])
            )
            return
        
        # Toggle status
        update_config = sync_to_async(lambda: Configuration.objects.filter(id=config_id).update(is_active=not config.is_active))
        await update_config()
        
        new_status = "فعال" if not config.is_active else "غیرفعال"
        text = f"✅ وضعیت کانفیگ {config.name} به {new_status} تغییر یافت."
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="manage_configs")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        print(f"❌ Error toggling config: {e}")
        await query.edit_message_text(
            "❌ خطا در تغییر وضعیت کانفیگ.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="manage_configs")]])
        )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from web app"""
    print(f"🔍 handle_webapp_data called!")
    
    if update.message and update.message.web_app_data:
        try:
            data = update.message.web_app_data.data
            user_id = update.effective_user.id
            
            print(f"🔍 WebApp data received from user {user_id}: {data}")
            
            # Get user
            get_user = sync_to_async(TelegramUser.objects.filter(telegram_id=user_id).first)
            user = await get_user()
            
            if not user or not user.is_verified:
                await update.message.reply_text("❌ شما مجاز به استفاده از این قابلیت نیستید.")
                return
            
            # Parse the data (assuming it's JSON)
            import json
            try:
                webapp_data = json.loads(data)
                print(f"🔍 Parsed webapp_data: {webapp_data}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                await update.message.reply_text("❌ خطا در پردازش اطلاعات دریافتی")
                return
            
            # Handle other webapp data (legacy)
            config_data = webapp_data
            
            # Create configuration
            create_config = sync_to_async(Configuration.objects.create)
            config = await create_config(
                user=user,
                name=f"کانفیگ {user.user_code}_{config_data.get('type', 'custom')}",
                description=config_data.get('description', ''),
                is_active=True
            )
            
            # Deduct balance
            cost = config_data.get('cost', 0)
            if user.balance >= cost:
                update_balance = sync_to_async(lambda: TelegramUser.objects.filter(id=user.id).update(balance=user.balance - cost))
                await update_balance()
                
                await update.message.reply_text(
                    f"✅ کانفیگ جدید با موفقیت ایجاد شد!\n\n"
                    f"🔧 نام کانفیگ: {config.name}\n"
                    f"💰 هزینه پرداخت شده: {cost} سکه\n"
                    f"💰 موجودی باقی‌مانده: {user.balance - cost} سکه\n\n"
                    f"کانفیگ شما فعال است و آماده استفاده می‌باشد."
                )
            else:
                await update.message.reply_text(
                    f"❌ موجودی ناکافی\n\n"
                    f"💰 هزینه مورد نیاز: {cost} سکه\n"
                    f"💰 موجودی شما: {user.balance} سکه\n\n"
                    f"لطفاً ابتدا موجودی خود را افزایش دهید."
                )
                
        except Exception as e:
            print(f"❌ Error handling web app data: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            await update.message.reply_text("❌ خطا در پردازش اطلاعات. لطفاً دوباره تلاش کنید.")
    else:
        print(f"❌ No web app data found in update")



def run_bot():
    global bot_app
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("menu", menu))
    bot_app.add_handler(CommandHandler("cart", cart))
    bot_app.add_handler(CallbackQueryHandler(handle_menu_selection, pattern="^add_"))
    bot_app.add_handler(CallbackQueryHandler(handle_cart_actions, pattern="^(remove_|confirm)"))
    bot_app.add_handler(CallbackQueryHandler(handle_panel_actions, pattern="^(create_config|wallet|my_configs|refresh_panel|channel|settings|report|rules|back_to_main|add_balance|transaction_history|manage_configs|change_name|notification_settings|usage_stats|financial_report|online_payment|toggle_config_)"))
    bot_app.add_handler(CommandHandler("adminweb", adminweb))
    bot_app.add_handler(CommandHandler("verify", verify_user))
    bot_app.add_handler(CommandHandler("addbalance", add_balance))
    bot_app.add_handler(CommandHandler("makeadmin", make_admin))
    bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    bot_app.run_polling()

if __name__ == "__main__":
    run_bot()
