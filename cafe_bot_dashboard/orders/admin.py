# orders/admin.py
from django.contrib import admin
from .models import Order, MenuItem

admin.site.register(MenuItem)
admin.site.register(Order)
