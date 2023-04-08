from rest_framework import serializers
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.shopping_cart.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'count', 'product')