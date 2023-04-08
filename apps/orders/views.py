from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import Order, OrderItem
from .serializers import *


class ListOrderView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-date_issued']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = 'transaction_id'
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)
