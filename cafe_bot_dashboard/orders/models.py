from django.db import models, transaction
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
import asyncio
import threading


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=150)
    telegram_username = models.CharField(max_length=100, blank=True)
    user_code = models.PositiveIntegerField(unique=True)
    is_verified = models.BooleanField(default=False)
    balance = models.PositiveIntegerField(default=0)  # Balance in coins
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def save(self, *args, **kwargs):
        if not self.user_code:
            # Generate sequential user codes starting from 10000
            try:
                # Use select_for_update to prevent race conditions
                with transaction.atomic():
                    # Get the highest existing user_code with row lock
                    highest_code = TelegramUser.objects.select_for_update().aggregate(
                        models.Max('user_code')
                    )['user_code__max']
                    
                    if highest_code is None:
                        # No users exist yet, start from 10000
                        self.user_code = 10000
                    else:
                        # Increment from the highest existing code
                        self.user_code = highest_code + 1
                        
            except Exception as e:
                # Fallback to 10000 if there's any error
                print(f"Warning: Error generating user code, using fallback: {e}")
                self.user_code = 10000
                
        super().save(*args, **kwargs)

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return f"{self.full_name} - {self.user_code}"

class VlessConfig(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='configs')
    vless_url = models.TextField()
    name = models.CharField(max_length=200, blank=True, null=True)  # Store config name/remark from external API
    created_at = models.DateTimeField(auto_now_add=True)
    total_bytes = models.BigIntegerField()
    used_bytes = models.BigIntegerField(default=0)  # Track used data
    expires_at = models.DateTimeField(null=True, blank=True)  # Expiration date
    is_active = models.BooleanField(default=True)  # Active status
    
    def get_remaining_bytes(self):
        """Get remaining bytes"""
        return max(0, self.total_bytes - self.used_bytes)
    
    def get_usage_percentage(self):
        """Get usage percentage"""
        if self.total_bytes == 0:
            return 0
        return min(100, (self.used_bytes / self.total_bytes) * 100)
    
    def is_expired(self):
        """Check if configuration is expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def get_days_remaining(self):
        """Get days remaining until expiration"""
        if not self.expires_at:
            return None
        from django.utils import timezone
        from datetime import timedelta
        remaining = self.expires_at - timezone.now()
        return max(0, remaining.days)

class Configuration(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='configurations')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.name}"


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.price}T"


class Cart(models.Model):
    customer_name = models.CharField(max_length=100)
    telegram_username = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Cart - {self.customer_name}"


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='orders')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('removed', 'Removed')
    ], default='new')

    def __str__(self):
        return f"{self.cart.customer_name} - {self.item.name}"


class SettlementReceipt(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='settlement_receipts')
    amount = models.PositiveIntegerField()
    image = models.ImageField(upload_to='receipts/')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_receipts')
    edited_amount = models.PositiveIntegerField(null=True, blank=True)

    def get_final_amount(self):
        return self.edited_amount if self.edited_amount is not None else self.amount

    def __str__(self):
        return f"{self.user.full_name} - {self.amount} - {'✔' if self.is_verified else '✖'}"


# Signal handlers for notifications
@receiver(post_save, sender=SettlementReceipt)
def handle_receipt_notifications(sender, instance, created, **kwargs):
    """Handle notifications for receipt creation and verification"""
    
    print(f"🔔 Signal triggered: created={created}, is_verified={instance.is_verified}, verified_at={instance.verified_at}")
    
    try:
        # Import here to avoid circular imports
        import requests
        import json
        
        # Bot token and notification functions
        BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"
        
        def send_telegram_message(chat_id, message):
            """Send message via Telegram Bot API"""
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            try:
                response = requests.post(url, json=data, timeout=10)
                print(f"📤 Telegram message sent to {chat_id}: {response.status_code}")
                if response.status_code != 200:
                    print(f"❌ Telegram API error: {response.text}")
                return response.status_code == 200
            except Exception as e:
                print(f"❌ Failed to send Telegram message: {e}")
                return False
        
        if created:
            print(f"📋 New receipt created for user {instance.user.full_name} (ID: {instance.user.telegram_id})")
            # New receipt created - notify admins
            admin_message = f"📋 <b>رسید جدید دریافت شد!</b>\n\n" \
                           f"👤 کاربر: {instance.user.full_name}\n" \
                           f"🆔 کد کاربری: <code>{instance.user.user_code}</code>\n" \
                           f"💰 مبلغ: <code>{instance.amount:,}</code> تومان\n" \
                           f"📅 تاریخ: {instance.created_at.strftime('%Y/%m/%d %H:%M')}\n\n" \
                           f"برای بررسی و تایید به پنل ادمین مراجعه کنید."
            
            # Get all admin users
            admin_users = TelegramUser.objects.filter(role='admin')
            print(f"👥 Found {admin_users.count()} admin users to notify")
            for admin in admin_users:
                print(f"📤 Sending notification to admin {admin.full_name} (ID: {admin.telegram_id})")
                success = send_telegram_message(admin.telegram_id, admin_message)
                if success:
                    print(f"✅ Notification sent successfully to {admin.full_name}")
                else:
                    print(f"❌ Failed to send notification to {admin.full_name}")
                
        elif instance.is_verified and instance.verified_at:
            print(f"✅ Receipt verified for user {instance.user.full_name} (ID: {instance.user.telegram_id})")
            # Receipt verified - notify user
            final_amount = instance.get_final_amount()
            user_message = f"✅ <b>رسید شما تایید شد!</b>\n\n" \
                          f"💰 مبلغ تایید شده: <code>{final_amount:,}</code> تومان\n" \
                          f"🆔 کد کاربری: <code>{instance.user.user_code}</code>\n" \
                          f"📅 تاریخ تایید: {instance.verified_at.strftime('%Y/%m/%d %H:%M')}\n\n" \
                          f"موجودی شما به‌روزرسانی شد و می‌توانید کانفیگ جدید خریداری کنید!"
            
            print(f"📤 Sending verification notification to user {instance.user.full_name} (ID: {instance.user.telegram_id})")
            success = send_telegram_message(instance.user.telegram_id, user_message)
            if success:
                print(f"✅ Verification notification sent successfully to {instance.user.full_name}")
            else:
                print(f"❌ Failed to send verification notification to {instance.user.full_name}")
            
    except Exception as e:
        print(f"❌ Error in receipt notification: {e}")
        import traceback
        traceback.print_exc()


class ConfigReport(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='reports')
    problem_description = models.TextField()
    has_tested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_reports')
    
    def __str__(self):
        return f"گزارش از {self.user.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# Signal handler for report notifications
@receiver(post_save, sender=ConfigReport)
def handle_report_notifications(sender, instance, created, **kwargs):
    """Handle notifications for report creation"""
    
    if created:
        try:
            import requests
            
            BOT_TOKEN = "8173740886:AAGKTILpDMFKNGGoswWNQDLFjy40QVsrCao"
            
            def send_telegram_message(chat_id, message):
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                try:
                    response = requests.post(url, json=data, timeout=10)
                    return response.status_code == 200
                except Exception as e:
                    print(f"❌ Failed to send Telegram message: {e}")
                    return False
            
            # Notify all admins about new report
            admin_message = f"📋 <b>گزارش جدید دریافت شد!</b>\n\n" \
                           f"👤 کاربر: {instance.user.full_name}\n" \
                           f"🆔 کد کاربری: <code>{instance.user.user_code}</code>\n" \
                           f"📝 مشکل: {instance.problem_description[:100]}{'...' if len(instance.problem_description) > 100 else ''}\n" \
                           f"🧪 تست شده: {'بله' if instance.has_tested else 'خیر'}\n" \
                           f"📅 تاریخ: {instance.created_at.strftime('%Y/%m/%d %H:%M')}\n\n" \
                           f"برای مشاهده جزئیات به پنل ادمین مراجعه کنید."
            
            admin_users = TelegramUser.objects.filter(role='admin')
            for admin in admin_users:
                send_telegram_message(admin.telegram_id, admin_message)
                
        except Exception as e:
            print(f"❌ Error in report notification: {e}")
