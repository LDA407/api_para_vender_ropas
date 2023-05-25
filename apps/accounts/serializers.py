from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model= User
        fields= ('id','email', 'full_name')


# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


from rest_framework import serializers
from apps.product.serializers import ProductSerializer
from .models import WishList, WishListItem

class WishListItemSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    product = ProductSerializer()
    
    class Meta:
        model = WishListItem
        fields = ['id','user', 'wishlist', 'product']


from rest_framework import serializers
from apps.product.serializers import ProductSerializer
from .models import Review
from apps.product.models import Product


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = Review
        fields = ['id','user', 'product', 'rating', 'comment']