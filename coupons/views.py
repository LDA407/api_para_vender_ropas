from rest_framework.views import APIView
from rest_framework import status
from .models import FixedPriceCoupon, PorcentageCoupon
from .serializers import FixedPriceCouponSerializer, PorcentageCouponSerializer
from rest_framework.response import Response

# Create your views here.

class CheckCouponView(APIView):
    def get(self, request, format=None):
        try:
            coupon_name = request.query_params.get('coupon_name')
            if FixedPriceCoupon.objects.filter(name = coupon_name).exists():
                coupon = FixedPriceCoupon.objects.get(name = coupon_name)
                coupon = FixedPriceCouponSerializer(coupon)
                return Response(
                    { 'coupon', coupon.data }, status=status.HTTP_200_OK
                )
            if PorcentageCoupon.objects.filter(name = coupon_name).exists():
                coupon = PorcentageCoupon.objects.get(name = coupon_name)
                coupon = PorcentageCouponSerializer(coupon)
                return Response(
                    { 'coupon', coupon.data }, status=status.HTTP_200_OK
                )
        except:
            return Response(
                {'error' : 'Something went wrong when checking coupon'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

