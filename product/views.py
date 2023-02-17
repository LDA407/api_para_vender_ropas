from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import permissions
from .models import Product
from .serializers import ProductSerializer
from django.db.models import Q
from .models import Category
from utils.responses import *


class ListCategoriesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, format=None):
        categories = Category.objects.all()

        if categories.exists():
            data = []
            for cat in categories:
                if not cat.parent:
                    sub_categories = [
                        {'id': sub_cat.id, 'name': sub_cat.name}
                        for sub_cat in categories
                        if sub_cat.parent and sub_cat.parent.id == cat.id
                    ]
                    data.append({'id': cat.id, 'name': cat.name, 'sub_categories': sub_categories})

            return success_response({'categories': data})
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, format=None):
        sortBy = request.query_params.get('sortBy')
        _PRODUCTS = Product.objects.all()

        if sortBy not in ["-date_created", "price", "sold", "name"]:
            sortBy = "date_created"

        order = request.query_params.get('order')
        limit = request.query_params.get('limit')

        if not limit:
            limit = 6
        
        # =====
        try: limit = int(limit);
        except ValueError:
            return bad_request({'Error': 'Not found'})
        
        # =====
        if order == "desc":
            sortBy = "-" + sortBy
            # filtrado y ordenado
            products = _PRODUCTS.order_by(sortBy).all()[:int(limit)]
        elif order == "asc":
            products = _PRODUCTS.order_by(sortBy).all()[:int(limit)]
        else:
            products = _PRODUCTS
        
        # =====
        products = ProductSerializer(products, many=True)
        if products:
            return success_response({'products': products.data})
        return not_found({'Error': 'Not product to the list'})


class DetailProductView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        product = get_object_or_404(Product, id=productId)
        product = ProductSerializer(product)
        return success_response({'product': product.data})


class SearchProductView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, format=None):
        data = request.data
        _PRODUCTS = Product.objects.all()
        _CATEGORIES = Category.objects.all()

        try:
            category_id = int(data['category_id'])
        except ValueError:
            return bad_request({'error': 'Category ID must be an integer'})

        search_query = data.get('search', '').strip()
        if search_query:
            search_result = _PRODUCTS.filter(
                Q(description__icontains=search_query) | Q(name__icontains=search_query))
        else:
            search_result = _PRODUCTS.order_by('-date_created')

        if category_id == 0:
            search_result = ProductSerializer(search_result, many=True)
            return success_response({'search_result': search_result.data})

        category = get_object_or_404(_CATEGORIES, id=category_id)

        if category.parent:
            search_result = search_result.filter(category=category)
        else:
            child_categories = _CATEGORIES.filter(parent=category)
            if not child_categories.exists():
                search_result = search_result.filter(category=category)
            else:
                filtered_categories = (category,) + tuple(child_categories)
                search_result = search_result.filter(category__in=filtered_categories)

        search_result = ProductSerializer(search_result.order_by('-date_created'), many=True)
        return success_response({'search_result': search_result.data})


class ListRelatedView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        try:
            product = Product.objects.get(id=productId)
        except Product.DoesNotExist:
            return not_found({'Error': 'Product not found'})

        category = product.category
        related_products = Product.objects.filter(category=category).exclude(id=productId).order_by('-sold')

        if not related_products.exists():
            return success_response({'Error': 'No related products found'})

        related_products = related_products[:3]
        related_products_serializer = ProductSerializer(related_products, many=True)

        return success_response(
            {'related_products': related_products_serializer.data},
        )


class FilterBySearchView(APIView):
    permission_classes = (permissions.AllowAny,)
    _CATEGORIES = Category.objects.all()
    _PRODUCTS = Product.objects.all()

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
            products_results = self._PRODUCTS
        
        elif not self._CATEGORIES.filter(id=category_id).exists():
            return not_found({'Error': 'Category not found'})
        
        else:
            category = self._CATEGORIES.get(id=category_id)
            if category.parent:
                products_results = self._PRODUCTS.filter(category=category)
            else:
                if not self._CATEGORIES.filter(parent=category).exists():
                    products_results = self._PRODUCTS.filter(category=category)
                else:
                    categories = self._CATEGORIES.filter(parent=category)
                    filtered_categories = tuple([category] + [c for c in categories])
                    # logger.debug(filtered_categories)
                    products_results = self._PRODUCTS.filter(category__in=filtered_categories)

        val1, val2 = price_range.split('-')
        if price_range == 'More then 80':
            products_results = products_results.filter(price__gte=80)
        else:
            products_results = products_results.filter(price__range=[val1, val2])

        products_results = products_results.order_by(sortBy, '-id')
        products_results = ProductSerializer(products_results, many=True)

        if products_results:
            return success_response({'filtered_products': products_results.data})
        return not_found({'Error': 'No products found'})