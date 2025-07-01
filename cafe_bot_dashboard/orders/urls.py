# orders/urls.py
from django.urls import path
from .views import CreateOrderView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view()),
]
