from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters, generics, pagination, permissions, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from utils.responses import *

from .models import *
from .serializers import *


class ListCategoriesView(generics.ListAPIView):
    queryset = Category.objects.filter(parent = None)
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    # renderer_classes = [JSONRenderer]
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date_created', 'price', 'sold', 'name']
    ordering = 'date_created'
    pagination_class = pagination.LimitOffsetPagination


class DetailProductView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = "id"


class SearchProductView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, format=None):
        data = request.data

        try:
            category_id = int(data['category_id'])
        except ValueError:
            return bad_request({'error': 'Category ID must be an integer'})

        search_query = data.get('search', '').strip()
        if search_query:
            search_result = Product.products.search_query(search_query)
        else:
            search_result = Product.objects.order_by('-date_created')

        if category_id == 0:
            search_result = ProductSerializer(search_result, many=True)
            return success_response(search_result.data)

        category = get_object_or_404(Category, id=category_id)

        if category.parent:
            search_result = search_result.filter(category=category)
        else:
            child_categories = Category.objects.filter(parent=category)
            if not child_categories.exists():
                search_result = search_result.filter(category=category)
            else:
                filtered_categories = (category,) + tuple(child_categories)
                search_result = search_result.filter(category__in=filtered_categories)

        search_result = ProductSerializer(search_result.order_by('-date_created'), many=True)
        return success_response(search_result.data)


class ListRelatedView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        id = self.kwargs["productId"]
            
        product = get_object_or_404(Product, id = id)
        queryset = Product.objects.filter(category = product.category).exclude(id = id).order_by('-sold')
        return queryset[:3]


class FilterBySearchView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        price_range = data['price_range']
        sortBy = data.get('sortBy', 'date_created')
        order = data.get('order')

        try:
            category_id = int(data['category_id'])
        except ValueError:
            return bad_request({'Error': 'Invalid category ID'})

        if sortBy not in ["date_created", "price", "sold", "name"]:
            sortBy = "date_created"

        if category_id == 0:
            products_results = Product.objects.all()
        
        elif not Category.objects.filter(id=category_id).exists():
            return not_found({'Error': 'Category not found'})
        
        else:
            category = Category.objects.get(id=category_id)
            if category.parent:
                products_results = Product.objects.filter(category=category)
            else:
                if not Category.objects.filter(parent=category).exists():
                    products_results = Product.objects.filter(category=category)
                else:
                    categories = Category.objects.filter(parent=category)
                    filtered_categories = tuple([category] + list(categories))
                    # logger.debug(filtered_categories)
                    products_results = Product.objects.filter(category__in=filtered_categories)
        
        if price_range == "More then 80":
            products_results = products_results.filter(price__gte=80)
        else:
            val1, val2 = price_range.split("-")
            products_results = products_results.filter(price__range=[val1, val2])

        products_results = products_results.order_by(sortBy, '-id')
        products_results = ProductSerializer(products_results, many=True)

        if products_results:
            return success_response(products_results.data)
        return not_found({'Error': 'No products found'})
