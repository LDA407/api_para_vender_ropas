from rest_framework import serializers
from models import FixedPriceCoupon, PorcentageCoupon

# Create your models here.
class FixedPriceCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedPriceCoupon
        fields = ('name', 'discount_code',)

    def __str__(self) -> str:
        return super().__str__()


class PorcentageCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = PorcentageCoupon
        fields = ('name', 'discount_porcentage',)

    def __str__(self) -> str:
        return super().__str__()