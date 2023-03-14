from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .models import Order, OrderItem
from apps.accounts.models import UserAccount
from apps.accounts.serializers import UserModelSerializer
from utils.responses import *


class ListOrderView(APIView):
    def get(self, request, format=None):
        user = request.user
        orders = Order.objects.all().order_by('-date_issued').filter(user = user)

        result = []
        for order in orders:
            result.append({
                'status': order.status,
                'transaction_id': order.transaction_id,
                'amount': order.amount,
                'shipping_price': order.shipping_price,
                'date_issued': order.date_issued 
            })

        if result:  # Si hay resultados retorna una respuesta exitosa con los resultados obtenidos 
            return success_response({'orders': result})
        return server_error({'error': 'something went wrong when retrieving orders'})


class OrderDetailView(APIView):
    def get(self, request, transactionID, format=None):
        user = request.user
        _ORDER = Order.objects.all()

        try:
            order = get_object_or_404(_ORDER, user = user, transaction_id = transactionID)
            if order:
                result = {
                    'status'         : order.status,
                    'transaction_id' : order.transaction_id,
                    'amount'         : order.amount,
                    'full_name'      : order.full_name,
                    'address_line_1' : order.address_line_1,
                    'address_line_2' : order.address_line_2,
                    'city'           : order.city,
                    'province'       : order.province,
                    'zip_code'       : order.zip_code,
                    'country'        : order.country,
                    'telephone'      : order.telephone,
                    'shipping_name'  : order.shipping_name,
                    'shipping_time'  : order.shipping_time,
                    'shipping_price' : order.shipping_price,
                    'date_issued'    : order.date_issued
                }
                order_items = OrderItem.objects.order_by('-date_issued').filter(order = order)
                result['order_items'] = [{
                    'name'     : item.name,
                    'price'    : item.price,
                    'count'    : item.count
                } for item in order_items ]
                return success_response({'order': result})
        except Exception:
            return server_error(
                {'error': 'something went wrong when retrieving orders'}
            )

