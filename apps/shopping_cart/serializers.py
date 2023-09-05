from rest_framework import serializers
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.shopping_cart.models import *


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'count', 'product')


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    # user = UserPublicSerializer(source='user', read_only=True)

    class Meta:
        model = Cart
        fields = (
            'id',
            'created_at',
            'user',
            'total',
            'items'
        )
    
    def get_items(self, obj):
        request = self.context.get('request')
        serializer = CartItemSerializer(obj.get_cart_items(), many=True, context={'request': request})
        return serializer.data

    def get_total(self, obj):
        data = str(obj.get_total_amount())
        return data