from django.shortcuts import get_list_or_404, get_object_or_404
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from rest_framework import permissions, viewsets, generics, filters
from rest_framework.views import APIView
from rest_framework import generics
from apps.shopping_cart.models import Cart, CartItem

from utils.responses import *

from .models import Review, WishList, WishListItem
from .serializers import *


# class UserProfileView(generics.ListCreateAPIView):
#     serializer_class = UserProfileSerializer
#     queryset = serializer_class.Meta.model.objects.all()


# class UserProfileManagementView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = UserProfile.objects.all()
#     serializer_class = UserProfileSerializer
#     lookup_field = "id"


class WishListView(generics.ListCreateAPIView):
    serializer_class = WishListSerializer
    queryset = serializer_class.Meta.model.objects.all()


class WishListManagementView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    lookup_field = "id"


class WishListItemCreateView(generics.ListCreateAPIView):
    serializer_class = WishListItemSerializer

    def get_queryset(self):
        # queryset = self.serializer_class.Meta.model.objects.filter(user_id = self.request.user)
        queryset = self.serializer_class.Meta.model.objects.all()
        return queryset

    # def perform_create(self, serializer):
    #     print(self.request.data)
    #     print(serializer.validated_data)
        # product = get_object_or_404(Product, id = product_id)
        # serializer.save(user = self.request.user, product = self.request.data["product"])


class WishListItemDestroyView(generics.DestroyAPIView):
    queryset = WishListItem.objects.all()
    serializer_class = WishListItemSerializer
    lookup_field = "id"


# class AddItemView(APIView):
    
# 	def post(self, request, format=None):
# 		user = self.request.user
# 		data = self.request.data

# 		try:
# 			product_id = int(data['prduct_id'])
# 		except ValueError:
# 			return bad_request({'error': 'The ID must be an integer'})
    
# 		try:
# 			product = get_object_or_404(Product, id = product_id)
# 			wishlist = get_object_or_404(WishList, user=user)
# 			wish_list_items = wishlist.get_wish_list_items()

# 			if wish_list_items[product]:
# 				return conflict_response({'error':'item already in wishlist'})
# 			else:
# 				WishListItem.objects.filter(user=user, wishlist=wishlist).update(product=product)
# 				wishlist.total_items =+ 1
# 				wishlist.save()

# 			cart = get_object_or_404(Cart, user = user)
# 			if cart._items_exists(product) :
# 				CartItem.objects.filter(cart=cart, product=product).delete()
# 			else:
# 				cart.total_items =- 1
# 				cart.save()
            
# 			# result = []
# 			# for item in wish_list_items:
# 			# 	product = get_object_or_404(Product, id = item.product.id)
# 			# 	product = ProductSerializer(product)
# 			# 	result.append({
# 			# 		'id': item.id,
# 			# 		'product': product.data,
# 			# 	})

# 			return success_response(WishListItemSerializer(wish_list_items, many=True).data)
# 		except Exception as error:
# 			return server_error({'error': f'{error}'})


class WishListItemDestroyView(generics.DestroyAPIView):
    queryset = WishListItem.objects.all()
    serializer_class = WishListItemSerializer
    lookup_field = "id"


class GetItemTotalView(APIView):

    def get(self, request):
        user = request.user

        try:
            wishlist = WishList.objects.get(user=user)
            total_items = wishlist.total_items
            return success_response({'total_items': total_items})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    filter_backends = [filters.SearchFilter,]
    search_fields = ['product__id']

    def perform_create(self, serializer):
        print(self.request.data)

        # product = get_object_or_404(Product, id = product_id)
        # serializer.save(user = self.request.user, product = self.request.data["product"])


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "id"


class FilterReview(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        product = get_object_or_404(Product, id=productId)
        rating = request.query_params.get('rating', None)

        try:
            if rating: rating = float(rating); rating = max(min(rating, 5.0), 0.5)
            else: rating = 5.0
            
            reviews = Review.objects.filter(
                product=product,
                rating__gte=rating-0.5,
                rating__lte=rating
            ).order_by('-created_at')

            data = ReviewSerializer(reviews, many=True).data
            return success_response(data)

        except Exception as error:
            return server_error({'error': f'{error}'})