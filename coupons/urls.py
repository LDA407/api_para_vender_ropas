from django.urls import path
from .views import CheckCouponView


app_name='coupons'
urlpatterns = [
	path('coupon', CheckCouponView.as_view()),
]