from rest_framework import serializers
from .models import Product

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
