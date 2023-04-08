from rest_framework import serializers
from apps.product.serializers import ProductSerializer
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    # user = serializers.CharField()
    product = ProductSerializer()
    
    class Meta:
        model = Review
        fields = ['id','user', 'product', 'rating', 'comment']