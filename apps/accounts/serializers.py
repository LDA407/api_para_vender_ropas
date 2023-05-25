from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from apps.product.models import Product
from apps.product.serializers import ProductSerializer

from .models import *

User = get_user_model()


class UserModelSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model= User
        fields= ('id','email', 'full_name')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class WishListItemSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    product = ProductSerializer()
    
    class Meta:
        model = WishListItem
        fields = ['id','user', 'wishlist', 'product']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = Review
        fields = ['id','user', 'product', 'rating', 'comment']