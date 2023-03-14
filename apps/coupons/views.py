from rest_framework.views import APIView
from .models import FixedPriceCoupon, PorcentageCoupon
from .serializers import FixedPriceCouponSerializer, PorcentageCouponSerializer
from backend.utils.responses import *
# Create your views here.

class CheckCouponView(APIView):
    def get(self, request, format=None):
        try:
            coupon_name = request.query_params.get('coupon_name')
            if FixedPriceCoupon.objects.filter(name = coupon_name).exists():
                coupon = FixedPriceCoupon.objects.get(name = coupon_name)
                coupon = FixedPriceCouponSerializer(coupon)
                return success_response({ 'coupon', coupon.data })

            if PorcentageCoupon.objects.filter(name = coupon_name).exists():
                coupon = PorcentageCoupon.objects.get(name = coupon_name)
                coupon = PorcentageCouponSerializer(coupon)
                return success_response({ 'coupon', coupon.data })

        except Exception as error:
            return server_error({'error' : f'Something went wrong when checking coupon: {str(error)}'})

