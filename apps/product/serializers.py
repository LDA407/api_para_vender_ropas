# -*- coding: utf-8 -*-

from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'children')
        read_only_fields = ('id',)
    
    def get_children(self, obj):
        serializer = CategorySerializer(obj.get_children(), many=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id',)


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ('id', 'name', 'tax_percentage')
        read_only_fields = ('id', 'products')


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ('id', 'products')


class GaleryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleryProduct
        fields = ('id', 'image', 'product', 'thumbnail')
        read_only_fields = ('id', 'product', 'thumbnail')


# class PublicGaleryProductSerializer(serializers.Serializer):
#     detail = serializers.HyperlinkedIdentityField(
#             view_name = 'product-detail',
#             lookup_field = 'pk',
#             context = {'request': request},
#             read_only=True
#     )
#     image = serializers.CharField(read_only=True)


class ColorVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorVariation
        fields = ('name',)
        read_only_fields = ('id',)


class SizeVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeVariation
        fields = ('name',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField(read_only = True)
    thumbnail = serializers.SerializerMethodField()
    taxes = serializers.SerializerMethodField(read_only = True)
    discount = serializers.SerializerMethodField(read_only = True)
    colors = serializers.SerializerMethodField(read_only = True)
    sizes = serializers.SerializerMethodField(read_only = True)
    # galerias = serializers.PrimaryKeyRelatedField(
	# 	many=True,
	# 	queryset=GaleryProduct.objects.all()
	# )
	# Tag = serializers.PrimaryKeyRelatedField(
	# 	many=True,
	# 	queryset=Tag.objects.all()
	# )
    # detail = serializers.HyperlinkedIdentityField(
    #     view_name = 'detail',
    #     lookup_field = 'id'
    # )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'colors',
            'sizes',
            'price',
            'category',
            'quantity',
            'sold',
            'date_created',
            'thumbnail',
            'taxes',
            'discount',
            'gallery'
        ]
        # read_only_fields = ('id',)

    def get_colors(self, obj):
        serializer = ColorVariationSerializer(obj.get_colors(), many = True)
        return serializer.data

    def get_sizes(self, obj):
        serializer = SizeVariationSerializer(obj.get_sizes(), many = True)
        return serializer.data
    
    def get_gallery(self, obj):
        serializer = GaleryProductSerializer(obj.get_gallery(), many = True)
        return serializer.data
    
    def get_thumbnail(self, obj):
        gallery = GaleryProduct.objects.filter(product_id = obj.id)
        if len(gallery) > 0:
            thumbnail = f"http://127.0.0.1:8000/media/{gallery[0].image}"
            return thumbnail
        return ''

    def get_taxes(self, obj):
        serializer = TaxSerializer(obj.get_taxes(), many = True)
        return serializer.data

    def get_discount(self, obj):
        str_discount = obj.get_discount()
        return str(str_discount)

