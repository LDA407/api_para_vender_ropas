from django.urls import path
from .views import ListOrderView, OrderDetailView

app_name = 'orders'

urlpatterns = [
	path('orders', ListOrderView.as_view() ),
	path('order/<transactionID>', OrderDetailView.as_view() )
]