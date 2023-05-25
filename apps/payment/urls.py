from django.urls import path
from .views import (
	GenerateTokenView,
	GetPaymentTotalView,
	ProcessPaymentView,
	ListOrderView,
	OrderDetailView
)


app_name='payment'

urlpatterns = [
	path('token', GenerateTokenView.as_view()),
	path('orders', ListOrderView.as_view() ),
	path('order/<transactionID>', OrderDetailView.as_view() )
	path('coupon', CheckCouponView.as_view()),
	path('payment_total', GetPaymentTotalView.as_view()),
	path('payment', ProcessPaymentView.as_view()),
]