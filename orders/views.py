from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .models import Order, OrderItem
from accounts.models import UserAccount
from accounts.serializers import UserModelSerializer
from utils.responses import *


# class ListOrderView2(ListAPIView):
# 	serializer_class = UserModelSerializer

# 	def dispatch(self, request, *args, **kwargs):
# 		return super().dispatch(request, *args, **kwargs)

# 	def get_queryset(self):
# 		get_object_or_404(user = self.request.user, order='-date_issued')#.order_by('-date_issued')
# 		return Order.objects.order_by('-date_issued').filter(user = self.request.user)

# 	def get(self, request, format=None):
# 		orders = self.get_queryset()
# 		# result = OrderSerializer(order, many=True) #esta es la forma mas sensilla de hacer estos
# 		result = []
# 		for order in orders:
# 			data = model_to_dict(order, fields=[
# 				'status', 'transaction_id', 'amount', 'shipping_price', 'date_issued'
# 			])
# 			result.append(data)
		
# 		return Response( {'orders': result}, status = status.HTTP_200_OK )



class ListOrderView(APIView):
	def get(self, request, format=None):
		user = request.user
		_ORDERS = Order.objects.all()
		try:
			orders = _ORDERS.order_by('-date_issued').filter(user = user)
			result = [
				{
					'status': order.status,
					'transaction_id': order.transaction_id,
					'amount': order.amount,
					'shipping_price': order.shipping_price,
					'date_issued': order.date_issued
				} for order in orders
			]
			return success_response({'orders': result})
		except Exception:
			return server_error({'error': 'something went wrong when retrieving orders'})


class OrderDetailView(APIView):
	def get(self, request, transactionID, format=None):
		user = request.user
		_ORDER = Order.objects.all()

		try:
			order = get_object_or_404(_ORDER, user = user, transaction_id = transactionID)
			if order:
				result = {
					'status': order.status,
					'transaction_id': order.transaction_id,
					'amount': order.amount,
					'full_name': order.full_name,
					'address_line_1': order.address_line_1,
					'address_line_2': order.address_line_2,
					'city': order.city,
					'province': order.province,
					'zip_code': order.zip_code,
					'country': order.country,
					'telephone': order.telephone,
					'shipping_name': order.shipping_name,
					'shipping_time': order.shipping_time,
					'shipping_price': order.shipping_price,
					'date_issued': order.date_issued
				}
				order_items = OrderItem.objects.order_by('-date_issued').filter(order = order)
				result['order_items'] = [{
					'name': item.name,
					'price': item.price,
					'count': item.count
				} for item in order_items ]
				return success_response({'order': result})
		except Exception:
			return server_error(
				{'error': 'something went wrong when retrieving orders'}
			)

