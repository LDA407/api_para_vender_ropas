from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import permissions
from shopping_cart.models import Cart, CartItem
from product.models import Product
from product.serializers import ProductSerializer
from .models import WishList, WishListItem
from utils.responses import *


class GetItemsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        user = self.request.user
        try:
            wishlist = WishList.objects.get(user = user)
            wishlist_items = WishListItem.objects.get(wishlist=wishlist)
            result = []
            if WishListItem.objects.filter(wishlist=wishlist).exists():
                for item in wishlist_items:
                    product = Product.objects.get(id=item.product.id)
                    product = ProductSerializer(product)
                    result.append({
                        'id': item.id,
                        'product': product.data,
                    })
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
            if Product.objects.filter(id = product_id).exists():
                return not_found({'error': f'the product with ID {product_id} does not exist'})
            
            product = Product.objects.get(id = product_id)
            wishlist = WishList.objects.get(user=user)

            if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                return conflict_response({'error':'item already in wishlist'})
            
            WishList.objects.create(
                user = user, wishlist = wishlist
            )

            if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                WishList.objects.filter(user=user).update(total_items =+ 1)
            
            cart = Cart.objects.get(user=user)

            if cart._cartitems_exists(cart, product):
                CartItem.objects.filter(cart=cart, product=product).delete()
            
                if not cart._cartitems_exists(cart, product):
                    Cart.objects.filter(user=user).update( total_items =-1 )
            
            wishlist_items = WishListItem.objects.filter(wishlist=wishlist)
            result = []
            for item in wishlist_items:
                product = Product.objects.get(id=item.product.id)
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
            if not Product.objects.filter(id=product_id).exists():
                return not_found({'error': f'The product with id {product_id} does not exist'})

            product = Product.objects.get(id = product_id)
            wishlist = WishList.objects.get(user=user)

            if not WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                return not_found({'error':'this product not in your wishlist'})
            
            WishListItem.objects.filter(
                wishlist = wishlist, product = product
            ).delete()

            if not WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
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
