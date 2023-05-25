from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters, generics, pagination, permissions
from rest_framework.views import APIView

from utils.responses import *

from .models import *
from .serializers import *


class ListCategoriesView(APIView):
    permission_classes = (permissions.AllowAny,)
    categories = Category.objects.all()

    def get(self, request, format=None):
        data = []
        for category in self.categories:
            sub_categories = Category.objects.filter(parent=category.id)
            data.append({
                'id': category.id,
                'name': category.name,
                'sub_categories': [{
                    'id': sub_category.id,
                    'name': sub_category.name,
                } for sub_category in sub_categories ]
            })
        return success_response(data)


class ProductListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date_created', 'price', 'sold', 'name']
    ordering = 'date_created'
    pagination_class = pagination.LimitOffsetPagination


# class ProductListView(APIView):
#     permission_classes = (permissions.AllowAny,)
#     def get(self, request, format=None):
#         

#         if sortBy not in ["-date_created", "price", "sold", "name"]:
#             sortBy = "date_created"

#         if not limit:
#             limit = 6
        
#         # =====
#         try: limit = int(limit);
#         except ValueError:
#             return bad_request({'Error': 'Not found'})
        
#         # =====
#         if order == "desc":
#             sortBy = "-" + sortBy
#             products = Product.objects.order_by(sortBy).all()[:int(limit)]
#         elif order == "asc":
#             products = Product.objects.order_by(sortBy).all()[:int(limit)]
#         else:
#             products = Product.objects.all()
        
#         # =====
#         products = ProductSerializer(products, many=True)
#         if products:
#             return success_response({'products': products.data})
#         return not_found({'Error': 'Not product to the list'})


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


class ListRelatedView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        product = get_object_or_404(Product, id=productId)
        category = product.category
        related_products = Product.objects.filter(category=category).exclude(id=productId).order_by('-sold')

        if not related_products:
            return success_response({'Error': 'No related products found'})

        related_products = related_products[:3]
        related_products_serializer = ProductSerializer(related_products, many=True)
        return success_response(related_products_serializer.data)


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
