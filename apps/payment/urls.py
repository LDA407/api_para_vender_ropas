from django.urls import path
from .views import (
	GenerateTokenView,
	GetPaymentTotalView,
	ProcessPaymentView
)

app_name='payment'

urlpatterns = [
	path('token', GenerateTokenView.as_view()),
	path('payment_total', GetPaymentTotalView.as_view()),
	path('payment', ProcessPaymentView.as_view()),
]