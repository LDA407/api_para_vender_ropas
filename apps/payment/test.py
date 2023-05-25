from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
import json


client = APIClient()

class OrderItemSerializerTestCase(TestCase):
    
    def setUp(self):
        self.orderitem = OrderItem.objects.create(
            id=1, product='test', name='test', price=100,
            count=1, data_added='2020-01-01'
        )
        
    def test_orderitem_serializer(self):
        serializer_data = OrderItemSerializer(instance=self.orderitem)
        self.assertEqual(serializer_data.data.get('name'), 'test')

class OrderSerializerTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='esxdcf@dfg.com',
            full_name='test_user',
            password='test_password'
        )
        self.order = Order.objects.create(
            id=1,
            status='test_status',
            user=self.user,
            transaction_id='test_transaction_id',
            amount=100,
            full_name='test_full_name',
            address_line_1='test_address_line_1',
            address_line_2='test_address_line_2',
            city='test_city',
            province='test_province',
            zip_code='test_zip_code',
            country='test_country',
            telephone='test_telephone',
            shipping_name='test_shipping_name',
            shipping_time='test_shipping_time',
            shipping_price=0,
            date_issued='2021-01-01',
            reference_number='test_reference_number',
        )

    def test_order_serializer(self):
        serializer_data = OrderSerializer(instance=self.order)
        self.assertEqual(serializer_data.data.get('status'), 'test_status')
        self.assertEqual(serializer_data.data.get('amount'), 100)
        
class ListOrderViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='esxdcf@dfg.com',
            full_name='test_user',
            password='test_password'
        )
        self.order = Order.objects.create(
            id=1,
            status='test_status',
            user=self.user,
            transaction_id='test_transaction_id',
            amount=100,
            full_name='test_full_name',
            address_line_1='test_address_line_1',
            address_line_2='test_address_line_2',
            city='test_city',
            province='test_province',
            zip_code='test_zip_code',
            country='test_country',
            telephone='test_telephone',
            shipping_name='test_shipping_name',
            shipping_time='test_shipping_time',
            shipping_price=0,
            date_issued='2021-01-01',
            reference_number='test_reference_number',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse('orders')
         
    def test_list_order_view(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)    

class OrderDetailViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='esxdcf@dfg.com',
            full_name='test_user',
            password='test_password'
        )
        self.order = Order.objects.create(
            id=1,
            status='test_status',
            user=self.user,
            transaction_id='test_transaction_id',
            amount=100,
            full_name='test_full_name',
            address_line_1='test_address_line_1',
            address_line_2='test_address_line_2',
            city='test_city',
            province='test_province',
            zip_code='test_zip_code',
            country='test_country',
            telephone='test_telephone',
            shipping_name='test_shipping_name',
            shipping_time='test_shipping_time',
            shipping_price=0,
            date_issued='2021-01-01',
            reference_number='test_reference_number',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = reverse('order_detail', kwargs={'transaction_id': self.order.transaction_id})
         
    def test_order_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data.get('status'), 'test_status')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


import json
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from .models import FixedPriceCoupon, PorcentageCoupon
from .serializers import FixedPriceCouponSerializer, PorcentageCouponSerializer
from utils.responses import *

class CheckCouponViewTestCase(APITestCase):
    url = "http://127.0.0.1:8000/api/coupons/coupon"

    def setUp(self):
        self.client = APIClient()
        self.fixed_price_coupon = FixedPriceCoupon.objects.create(
            name='FIXEDCODE', discount_amount=10)
        self.porcentage_coupon = PorcentageCoupon.objects.create(
            name='PORCENCODE', discount_porcentage=0.15)

    def test_get_coupon_success(self):
        
        response = self.client.get(f"{self.url}?coupon_name={self.fixed_price_coupon.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'coupon': FixedPriceCouponSerializer(self.fixed_price_coupon).data})
        
        response = self.client.get(f"{self.url}?coupon_name={self.porcentage_coupon.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), { 'coupon': PorcentageCouponSerializer(self.porcentage_coupon).data })
        
    def test_get_coupon_failure(self):
        response = self.client.get(f"{self.url}?coupon_name=INVALIDCOUPON")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
