# orders/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MenuItem, Order
from .serializers import OrderSerializer

class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # لاگ خطا برای دیباگ
            print("❌ Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
