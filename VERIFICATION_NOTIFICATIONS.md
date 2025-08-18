# User Verification Notification System

This document explains how the user verification notification system works in the RCOINX Telegram Bot.

## Overview

When a new user starts the bot and waits for admin approval, they will automatically receive a notification once they are verified by an admin. This notification informs them that their account has been approved and they can now use all bot features.

## How It Works

### 1. User Registration
- New users start the bot with `/start`
- They are added to the database with `is_verified=False`
- They receive a message asking them to wait for admin approval

### 2. Admin Verification
Admins can verify users through multiple methods:
- **Telegram Bot Command**: `/verify <user_code>`
- **Web Admin Panel**: Toggle verification status in the admin interface
- **API Endpoint**: `POST /admin-api/user-verify/`

### 3. Automatic Notification
When a user is verified:
- The system detects the verification status change
- Automatically sends a congratulatory message to the user
- Includes their user code and instructions to start using the bot

## Implementation Details

### Files Modified

1. **`cafe_bot_dashboard/orders/notifications.py`** - New utility module for notifications
2. **`cafe_bot_dashboard/orders/views.py`** - Updated verification views
3. **`main.py`** - Bot already had notification functions

### Key Functions

#### `send_verification_notification(user)`
- Sends congratulatory message to verified user
- Includes user name, code, and next steps
- Uses HTML formatting for better presentation

#### `toggle_verify()` and `admin_user_verify()`
- Handle verification status changes
- Automatically trigger notifications when users are verified
- Prevent duplicate notifications

## Message Format

The verification notification includes:
```
🎉 تبریک! حساب کاربری شما تایید شد!

👤 نام: [User Full Name]
🆔 کد کاربری: [User Code]

✅ حالا می‌توانید از تمام امکانات ربات استفاده کنید!

برای شروع، دستور /start را ارسال کنید.
```

## Testing

### Test Notification System
```bash
python test_verification_notification.py
```

### Test Admin Verification
```bash
python test_admin_verification.py
```

## Configuration

The bot token is configured in `cafe_bot_dashboard/orders/notifications.py`:
```python
BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"
```

## Error Handling

- Failed notifications are logged with detailed error messages
- System continues to function even if notifications fail
- All errors are captured and logged for debugging

## Security

- Only admin users can verify other users
- Verification status changes are logged
- Notifications are sent directly to verified users only

## Future Enhancements

- Add notification preferences for users
- Support for different notification types
- Integration with external notification services
- Notification delivery status tracking
