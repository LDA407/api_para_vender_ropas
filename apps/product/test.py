from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.test import APIClient
from .models import Product, Category
from .serializers import ProductSerializer
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory
from .views import SearchProductView


class ProductListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(
            name="Product 1", description="Description 1",
            price=10.0, category=get_object_or_404(Category, id = 4),
            quantity=2243, sold=3, 
            date_created="2012-02-06 00:00:00.000"
        )
        self.product2 = Product.objects.create(
            name="Product 2", description="Description 2",
            price=20.0, category=get_object_or_404(Category, id = 2),
            quantity=2323, sold=3, 
            date_created="2012-02-06 00:00:00.000"
        )
        self.product3 = Product.objects.create(
            name="Product 3", description="Description 3",
            price=30.0, category=get_object_or_404(Category, id = 14),
            quantity=232, sold=3, 
            date_created="2012-02-06 00:00:00.000"
        )

    def test_get_all_products(self):
        response = self.client.get(reverse('product-list'))
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_products_by_name(self):
        data = {'search': '2'}
        response = self.client.get(reverse('product-list'), data=data)
        products = Product.objects.filter(name__icontains='2')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_products_by_description(self):
        data = {'search': '3'}
        response = self.client.get(reverse('product-list'), data=data)
        products = Product.objects.filter(description__icontains='3')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sort_products_by_price(self):
        data = {'ordering': 'price'}
        response = self.client.get(reverse('product-list'), data=data)
        products = Product.objects.all().order_by('price')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination(self):
        data = {'limit': 2, 'offset': 0}
        response = self.client.get(reverse('product-list'), data=data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            description='This is a test product.',
            price=29.99,
            category=Category.objects.create(name='Test Category'),
            quantity=10,
            sold=5
        )

    def test_product_creation(self):
        self.assertTrue(isinstance(self.product, Product))
        self.assertEqual(str(self.product), self.product.name)


class SearchProductViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SearchProductView.as_view()
        self.category = Category.objects.create(name='Test Category')
        self.product_1 = Product.objects.create(
            name='Test Product 1',
            description='This is a test product 1.',
            price=29.99,
            category=self.category,
            quantity=10,
            sold=5
        )
        self.product_2 = Product.objects.create(
            name='Test Product 2',
            description='This is a test product 2.',
            price=39.99,
            category=self.category,
            quantity=5,
            sold=2
        )
        self.product_3 = Product.objects.create(
            name='Another Product',
            description='This is another test product.',
            price=19.99,
            category=self.category,
            quantity=20,
            sold=10
        )

    def test_search_product_view_with_search_query(self):
        request = self.factory.post('/search/', {'search': 'test'})
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['search_result']), 2)

    def test_search_product_view_with_category(self):
        request = self.factory.post('/search/', {'category_id': self.category.id})
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['search_result']), 3)

    def test_search_product_view_with_invalid_category_id(self):
        request = self.factory.post('/search/', {'category_id': 'invalid'})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Category ID must be an integer', response.data['error'])
