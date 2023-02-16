from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Product
from .serializers import ProductSerializer
from django.db.models import Q
from .models import Category


class ListCategoriesView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
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

            return Response({'categories': data}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_204_NO_CONTENT)




class ProductListView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, format=None):
        sortBy = request.query_params.get('sortBy')
        _PRODUCTS = Product.objects

        if sortBy not in ["-date_created", "price", "sold", "name"]:
            sortBy == "date_created"
        
        # show by order or limit 
        order = request.query_params.get('order')
        limit = request.query_params.get('limit')

        if not limit:
            limit = 6
        
        # =====
        
        try: limit = int(limit);
        except:
            return Response(
                {'Error': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # =====

        if order == "desc":
            sortBy = "-" + sortBy
            # filtrado y ordenado
            products = _PRODUCTS.order_by(sortBy).all()[:int(limit)]
        elif order == "asc":
            products = _PRODUCTS.order_by(sortBy).all()[:int(limit)]
        else:
            products = _PRODUCTS.all()
        
        # =====

        products = ProductSerializer(products, many=True)
        if products:
            return Response(
                {'products': products.data}, status=status.HTTP_200_OK
            )
        return Response(
            {'Error': 'Not product to the list'},
            status=status.HTTP_404_NOT_FOUND
        )



class DetailProductView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, productId, format=None):
        try: product_id=int(productId)
        except:
            return Response(
                {'Error': 'Product Id not found'},
                status=status.HTTP_404_NOT_FOUND 
            )
        
        product = get_object_or_404(Product, id=product_id)
        product = ProductSerializer(product)
        return Response(
            {'product': product.data}, status=status.HTTP_200_OK
        )


class SearchProductView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data
        _PRODUCTS = Product.objects.all()
        _CATEGORIES = Category.objects.all()

        try:
            category_id = int(data['category_id'])
        except ValueError:
            return Response(
                {'error': 'Category ID must be an integer'},
                status=status.HTTP_400_BAD_REQUEST)

        search_query = data.get('search', '').strip()
        if search_query:
            search_result = _PRODUCTS.filter(
                Q(description__icontains=search_query) | Q(name__icontains=search_query))
        else:
            search_result = _PRODUCTS.order_by('-date_created')

        if category_id == 0:
            search_result = ProductSerializer(search_result, many=True)
            return Response({'search_result': search_result.data}, status=status.HTTP_200_OK)

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
        return Response({'search_result': search_result.data}, status=status.HTTP_200_OK)



# class ListRelatedView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def get(self, request, productId, format=None):
#         try: product_id = int(productId)
#         except:
#             return Response(
#                 {'Error': 'Product Id not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         #=====

#         category = get_object_or_404(Product, id=product_id).category
#         if Product.objects.filter(category=category).exists():
#             if category.parent:
#                 related_products = Product.objects.order_by('-sold').filter(category=category)
#             else:
#                 #si la categoria padre no tiene hijos, filtra solo la categoria
#                 if not Category.objects.filter(parent=category).exists():
#                     related_products = Product.objects.order_by('-sold').filter(category=category)
#                 else:
#                     categories = Category.objects.filter(parent=category)
#                     filtered_categories = tuple([category], [filtered_categories.append(c) for c in categories])
#             #=====

#             # excluir el producto actual
#             related_products = related_products.exclude(id=product_id)
#             related_products = ProductSerializer(related_products, many=True)

#             if len(related_products.data) > 3:
#                 return Response(
#                     {'related_products': related_products.data[:3]},
#                     status=status.HTTP_200_OK
#                 )
#             elif len(related_products.data) > 0:
#                 return Response(
#                     {'related_products': related_products.data},
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 return Response(
#                     {'Error': 'No relaed product found'},
#                     status=status.HTTP_200_OK
#                 )
#         else:
#             return Response(
#                 {'Error': 'No relaed product found'},
#                 status=status.HTTP_200_OK
#             )


class ListRelatedView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)
        except ValueError:
            return Response(
                {'Error': 'Invalid product Id'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'Error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        category = product.category
        related_products = Product.objects.filter(category=category).exclude(id=product_id).order_by('-sold')

        if not related_products.exists():
            return Response(
                {'Error': 'No related products found'},
                status=status.HTTP_200_OK
            )

        related_products = related_products[:3]
        related_products_serializer = ProductSerializer(related_products, many=True)

        return Response(
            {'related_products': related_products_serializer.data},
            status=status.HTTP_200_OK
        )






# class FilterBySearchView(APIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         data = self.request.data
#         price_range = data['price_range']
#         sortBy = data['sortBy']
#         order = data['order']
#         #=====

#         try: category_id = int(data['category_id']);
#         except:
#             return Response(
#                 {'Error': 'Category ID must bee an integer'},
#                 status=status.HTTP_404_NOT_FOUND )
#         #=====

#         if sortBy not in ["date_created", "price", "sold", "name"]:
#             sortBy == "date_created"
#         # =====
        
#         if category_id == 0:
#             products_results = Product.objects.all()
#         elif not Category.objects.filter(id=category_id).exists():
#             return Response(
#                 {'Error': 'This category does not exist'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         else:
#             category = Category.objects.get(id=category_id)
#             if category.parent:
#                 products_results = Product.objects.filter(category=category)
#             else:
#                 #si la categoria padre no tiene hijos, filtra solo la categoria
#                 if not Category.objects.filter(parent=category).exists():
#                     products_results = Product.objects.filter(category=category)
#                 else:
#                     categories = Category.objects.filter(parent=category)
#                     filtered_categories = tuple([category], [filtered_categories.append(c) for c in categories])
#                     print(filtered_categories)
#                     products_results = Product.objects.filter(category_in=filtered_categories)

#         for i in ['1-19', '20-39', '40-59', '60-79']:
#             if i == price_range:
#                 val1 = float(price_range.split('-')[0])
#                 val2 = float(price_range.split('-')[1])
#                 print(f"val1: {val1}, val2: {val2}")
#                 products_results = products_results.filter(price__gte=val1)
#                 products_results = products_results.filter(price__lt=val2)
#         if price_range == 'More then 80':
#             products_results = products_results.filter(price__gte=80)
#         # =====
        
#         # filtrar por sortBy
#         if order == 'desc':
#             sortBy = '-' + sortBy
#             # filtrado y ordenado
#             products_results = products_results.order_by(sortBy) 
#         elif order == 'asc':
#             products_results = products_results.order_by(sortBy)
#         else:
#             products_results = products_results.order_by(sortBy)
        
#         products_results = ProductSerializer(products_results, many=True)
#         #=====

#         if len(products_results.data) > 0:
#             return Response(
#                 {'filtered_products': products_results.data},
#                 status=status.HTTP_200_OK
#             )
#         return Response(
#             {'Error': 'No products found'},
#             status=status.HTTP_200_OK
#         )



class FilterBySearchView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = self.request.data
        price_range = data['price_range']
        sortBy = data.get('sortBy', 'date_created')
        order = data['order']

        try:
            category_id = int(data['category_id'])
        except:
            return Response(
                {'Error': 'Invalid category ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if sortBy not in ["date_created", "price", "sold", "name"]:
            sortBy = "date_created"

        if category_id == 0:
            products_results = Product.objects.all()
        elif not Category.objects.filter(id=category_id).exists():
            return Response(
                {'Error': 'Category not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            category = Category.objects.get(id=category_id)
            if category.parent:
                products_results = Product.objects.filter(category=category)
            else:
                if not Category.objects.filter(parent=category).exists():
                    products_results = Product.objects.filter(category=category)
                else:
                    categories = Category.objects.filter(parent=category)
                    filtered_categories = tuple([category] + [c for c in categories])
                    logger.debug(filtered_categories)
                    products_results = Product.objects.filter(category__in=filtered_categories)


        val1, val2 = price_range.split('-')
        if price_range == 'More then 80':
            products_results = products_results.filter(price__gte=80)
        else:
            products_results = products_results.filter(price__range=[val1, val2])

        products_results = products_results.order_by(sortBy, '-id')
        products_results = ProductSerializer(products_results, many=True)

        if products_results:
            return Response(
                {'filtered_products': products_results.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'Error': 'No products found'},
            status=status.HTTP_200_OK
        )
