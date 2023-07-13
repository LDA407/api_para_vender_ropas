from rest_framework import serializers
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.shopping_cart.models import *


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'count', 'product')

    def create(self, validated_data):
        user = validated_data.pop('user')
        return self.Meta.model.objects.create(user = user, **validated_data)


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
        serializer = CartItemSerializer(obj.get_cart_items(), many=True)
        return serializer.data

    def get_total(self, obj):
        data = str(obj.get_total_amount())
        return data