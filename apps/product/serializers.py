from rest_framework import serializers
from .models import *


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = (,)
#         read_only_fields = ('id',)


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = (,)
#         read_only_fields = ('id',)


# class TaxSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tax
#         fields = (,)
#         read_only_fields = ('id',)


# class DiscountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Discount
#         fields = (,)
#         read_only_fields = ('id',)


# class GaleryProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GaleryProduct
#         fields = (,)
#         read_only_fields = ('id',)


# class ColorVariationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ColorVariation
#         fields = (,)
#         read_only_fields = ('id',)


# class SizeVariationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SizeVariation
#         fields = (,)
#         read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    # photo = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'quantity',
            'sold',
            'galery',
            'date_created',
            # 'get_image',
        ]
        read_only_fields = ('id',)
    
    # def create(self, validated_data):
    #     product = Product.objects.create(**validated_data)
    #     return product

    # def update(self, instance, validated_data):
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.content = validated_data.get('content', instance.content)
    #     instance.created = validated_data.get('created', instance.created)
    #     instance.save()
    #     return instance
