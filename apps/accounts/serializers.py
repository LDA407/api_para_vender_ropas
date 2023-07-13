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
        fields= (
            'id',
            'email',
            'full_name'
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class WishListItemSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    product = ProductSerializer()
    
    class Meta:
        model = WishListItem
        fields = (
            'id',
            'user',
            'wishlist',
            'product'
        )

    # def create(self, validated_data):
    #     user = validated_data.pop('user')
    #     return Review.objects.create(user = user, **validated_data)

    # def update(self, instance, validated_data):
    #     instance.rating = validated_data.get('rating', instance.rating)
    #     instance.comment = validated_data.get('comment', instance.comment)
    #     instance.save()
    #     return instance

    # def delete(self, instance):
    #     instance.delete()


class WishListSerializer(serializers.ModelSerializer):
    # items = serializers.SerializerMethodField()

    class Meta:
        model = WishList
        fields = (
            'id',
            'user',
            'total_items',
            # 'items'
        )
        read_only_fields = ('id',)
    
    # def get_iems(self, obj):
    #     children = obj.wishlistitems._set.all()
    #     serializer = WishListItemSerializer(children, many=True)
    #     return serializer.data




class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    product = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.all()
    )
    
    class Meta:
        model = Review
        fields = (
            'id',
            'user',
            'product',
            'rating',
            'comment'
        )

    # def create(self, validated_data):
    #     user = validated_data.pop('user')
    #     return Review.objects.create(user = user, **validated_data)

    # def update(self, instance, validated_data):
    #     instance.rating = validated_data.get('rating', instance.rating)
    #     instance.comment = validated_data.get('comment', instance.comment)
    #     instance.save()
    #     return instance

    # def delete(self, instance):
    #     instance.delete()


