# orders/serializers.py
from .models import Order, Cart, MenuItem
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'