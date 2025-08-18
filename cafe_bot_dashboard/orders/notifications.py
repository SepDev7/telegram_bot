import requests
import logging

logger = logging.getLogger(__name__)

# Bot token for notifications - will be imported from config
from config import BOT_TOKEN

def send_telegram_message(chat_id, message, parse_mode="HTML"):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Telegram message sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message to {chat_id}: {e}")
        return False

def send_verification_notification(user):
    """Send verification notification to a user"""
    user_message = f"🎉 <b>تبریک! حساب کاربری شما تایید شد!</b>\n\n" \
                  f"👤 نام: {user.full_name}\n" \
                  f"🆔 کد کاربری: <code>{user.user_code}</code>\n\n" \
                  f"✅ حالا می‌توانید از تمام امکانات ربات استفاده کنید!\n\n" \
                  f"برای شروع، دستور /start را ارسال کنید."
    
    success = send_telegram_message(user.telegram_id, user_message)
    if success:
        logger.info(f"✅ Verification notification sent to user {user.full_name}")
    else:
        logger.error(f"❌ Failed to send verification notification to {user.full_name}")
    
    return success
