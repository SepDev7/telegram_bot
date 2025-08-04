# # orders/admin.py
# from django.contrib import admin
# from .models import Order, MenuItem

# admin.site.register(MenuItem)
# admin.site.register(Order)

# orders/admin.py
from django.contrib import admin
from .models import MenuItem, Order, Cart, TelegramUser, VlessConfig


class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "telegram_username", "user_code", "is_verified", "role")
    list_filter = ("is_verified", "role")
    search_fields = ("full_name", "telegram_username", "user_code")
    
    def get_role(self, obj):
        return obj.role
    get_role.short_description = "Role"


admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(VlessConfig)




