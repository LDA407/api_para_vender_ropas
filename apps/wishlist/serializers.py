from rest_framework import serializers
from apps.product.serializers import ProductSerializer
from .models import WishList, WishListItem

class WishListItemSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    product = ProductSerializer()
    
    class Meta:
        model = WishListItem
        fields = ['id','user', 'wishlist', 'product']