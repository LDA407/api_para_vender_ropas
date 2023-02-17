from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'price', 'count', 'data_added']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'user', 'transaction_id', 'amount', 'full_name',
                  'address_line_1', 'address_line_2', 'city', 'province', 'zip_code',
                  'country', 'telephone', 'shipping_name', 'shipping_time', 'shipping_price',
                  'date_issued', 'reference_number', 'items']
        read_only_fields = ['id', 'user', 'transaction_id', 'amount', 'date_issued', 'reference_number']
