# orders/models.py
from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.name} - {self.price}T"

class Order(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    telegram_username = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('done', 'Done')
    ], default='new')

    def __str__(self):
        return f"{self.customer_name} - {self.item.name}"
