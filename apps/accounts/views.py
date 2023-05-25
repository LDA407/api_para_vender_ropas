from django.shortcuts import get_list_or_404, get_object_or_404
from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from rest_framework import permissions
from rest_framework.views import APIView
from apps.shopping_cart.models import Cart, CartItem

from utils.responses import *

from .models import Review, WishList, WishListItem
# from .models import UserProfile
from .serializers import *

# class GetUserProfileView(APIView):
#     def get(self, request, format=None):
#         try:
#             user_profile = get_object_or_404(UserProfile, user = self.request.user)
#             user_profile = UserProfileSerializer(user_profile)
#             return success_response({'profile': user_profile.data})
#         except Exception as e:
#             return server_error({'error': f'{e}'})


# class UdateUserProfile(APIView):
#     def put(self, request, format=None):
#         try:
#             user = self.request.user
#             data = self.request.data

#             UserProfile.objects.filter(user=user).update(**data)

#             user_profile = UserProfile.objects.filter(user=user)
#             user_profile = UserProfileSerializer(user_profile)

#             return success_response({'profile': user_profile.data})
#         except Exception as e:
#             return server_error({'error': f'{e}'})


class GetItemsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        try:
            wishlist = get_object_or_404(WishList, user = self.request.user)
            wishlist_items = get_object_or_404(WishListItem, wishlist=wishlist)
            result = WishListItemSerializer(wishlist_items, many = True)
            return success_response({'wishlist': result})
        except Exception as error:
            return server_error({'error': f'{error}'})


class AddItemView(APIView):
    
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            product_id = int(data['prduct_id'])
        except ValueError:
            return bad_request({'error': 'The ID must be an integer'})
    
        try:
            product = get_object_or_404(Product, id = product_id)
            wishlist = get_object_or_404(WishList, user=user)

            if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                return conflict_response({'error':'item already in wishlist'})
            
            WishList.objects.create(
                user = user, wishlist = wishlist
            )

            if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                WishList.objects.filter(user=user).update(total_items =+ 1)
            
            cart = get_object_or_404(Cart, user = user)

            cart_exists = cart._items_exists(cart, product) 

            if cart_exists:
                CartItem.objects.filter(cart=cart, product=product).delete()
            
                if not cart_exists:
                    Cart.objects.filter(user=user).update( total_items =-1 )
            
            wishlist_items = WishListItem.objects.filter(wishlist=wishlist)
            result = []
            for item in wishlist_items:
                product = get_object_or_404(Product, id = item.product.id)
                product = ProductSerializer(product)
                result.append({
                    'id': item.id,
                    'product': product.data,
                })

            return success_response({'wishlist': result})
        except Exception as error:
            return server_error({'error': f'{error}'})


class GetItemTotalView(APIView):

    def get(self, request):
        user = request.user

        try:
            wishlist = WishList.objects.get(user=user)
            total_items = wishlist.total_items
            return success_response({'total_items': total_items})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class RemoveItemView(APIView):
    def delete(self, request, format=None):
        user = request.user
        data = request.data

        try:
            product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error': 'El id del producto debe ser un entero'})

        try:

            product = get_object_or_404(Product, id = product_id)
            wishlist = get_object_or_404(WishList, user=user)

            wishlist_exists = WishListItem.objects.filter(wishlist=wishlist, product=product).exists()

            if not wishlist_exists:
                return not_found({'error':'this product not in your wishlist'})
            
            WishListItem.objects.filter(
                wishlist = wishlist, product = product
            ).delete()

            if not wishlist_exists:
                WishList.objects.filter(user=user).update(total_items =- 1)
            
            wishlist_items = WishListItem.objects.filter(wishlist=wishlist)
            
            result = []
            if WishListItem.objects.filter(wishlist=wishlist).exists():
                for item in wishlist_items:
                    product = Product.objects.get(id=item.product.id)
                    product = ProductSerializer(product)
                    result.append({
                        'id': item.id,
                        'product': product.data,
                    })
                return success_response({'cart': result})

        except Exception as error:
            return server_error({'error': f'Algo salió mal al eliminar el elemento del carrito: {str(error)}'})


class GetReview(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, productId, format=None):
        try:
            product = get_object_or_404(Product, id = productId)
            reviews = get_list_or_404(Review, product=product)
            data = list(ReviewSerializer(reviews, many = True).data)
            return success_response(data)
        
        except Exception as error:
            return server_error({'error': f'{error}'})


class CreateReview(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, productId, format=None):
        user = request.user
        data = request.data
        product = get_object_or_404(Product, id = productId)

        if Review.objects.filter(user=user, product=product).exists():
            return conflict_response({'error': f'A review for this product has already been created'})

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # serializer.save(user=user, product=product)
            review = serializer.data

            reviews = Review.objects.order_by('-created_at').filter(product=product)
            results = ReviewSerializer(reviews, many=True).data
            return created_response({'review': review, 'reviews': results})
        return bad_request(serializer.errors)


class UpdateReview(APIView):
    def put(self, request, productId, format=None):
        user = self.request.user
        data = self.request.data

        try: rating = float(data.get('rating'))
        except ValueError:
            return bad_request({'error': 'Rating must be a decimal value'})
        # ====================

        try: comment = str(data.get('comment'))
        except ValueError:
            return bad_request({'error': 'Must pass a comment when creating review'})
        # ====================
        
        try:
            product = get_object_or_404(Product, id = productId)
            if not Review.objects.filter(user = user, product = product).exists():
                return conflict_response({'error': 'The review for this product does not exist'})
            
            serializer = ReviewSerializer(rating = rating, comment = comment)
            if serializer.is_valid():
                serializer.save(user=user, product=product)
                review = serializer.data
                reviews = Review.objects.order_by('-created_at').filter(product=product)
                results = ReviewSerializer(reviews, many=True).data
                return created_response({'review': review, 'reviews': results})
            return not_content({'error': "no reviews"})
        except Exception as error:
            return server_error({'error': f'{error}'})


class DeleteReview(APIView):
    def delete(self, request, productId, format=None):
        product = get_object_or_404(Product, id = productId)
        review = get_object_or_404(Review, user = self.request.user, product=product)
        review.delete()

        reviews = Review.objects.order_by('-created_at').filter(product = product)
        data = ReviewSerializer(reviews, many = True).data
        return success_response(data)


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