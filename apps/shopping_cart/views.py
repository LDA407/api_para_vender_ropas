from django.db import IntegrityError
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from utils.responses import *
from utils.shpping_cart.serializers import *

from .models import Cart, CartItem


class GetItemsView(ListAPIView):
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        cart = get_object_or_404(Cart, user = self.request.user)
        return cart.cartitem_set.select_related('product').order_by('product_id')


class AddItemView(APIView):

    def post(self, request):
        user = request.user
        data = request.data
        count = 1
        
        try: product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error': 'the id must be an integer'})
        try:
            cart = get_object_or_404(Cart, user = user)
            product = get_object_or_404(Product, id=product_id)

            if cart._item_exists(product):
                return conflict_response({'error':'the product already in cart'})

            if int(product.quantity) > 0:
                CartItem.objects.create(product = product, cart = cart, count = count)

                if cart._item_exists(product):
                    Cart.objects.filter(user = user).update(total_items =+ 1)
                    cart_items = CartItem.objects.order_by('product').filter(cart = cart)
                    serializer = CartItemSerializer(cart_items, many = True)
                    return created_response(serializer.data)
                return success_response({'error': 'no enough of this item in stock'})
        # except IntegrityError:
        #     return Response({'error': 'no enough of this item in stock'}, status=status.HTTP_200_OK)
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class GetTotalView(APIView):
    def get(self, request):
        try:
            cart = get_object_or_404(Cart, user = request.user)
            costo_total = cart.get_total_amount()
            # total_compare_amount = cart.get_total_compare_amount()
            return success_response({
                'costo_total': costo_total,
                # 'total_con_descuentos': total_compare_amount
            })

        except Exception as error:
            return server_error({'error': f'something went wrong: {str(error)}'})


class GetItemTotalView(APIView):

    def get(self, request):
        cart =  get_object_or_404(Cart, user = request.user )
        return success_response({'total_items': cart.total_items})


class UpdateItemView(APIView):
    def put(self, request, format=None):
        data = request.data

        try: product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error':'the id must be an integer'})

        try: count = int(data.get('count'))
        except ValueError:
            return bad_request({'error':'count must be an integer'})
        
        try:
            product = get_object_or_404(Product, id = product_id )
            cart =  get_object_or_404(Cart, user = request.user )

            if not cart._item_exists(product):
                return not_found({'error':'El producto no esta en tu carrito'})

            if count <= product.quantity:
                CartItem.objects.filter(cart = cart, product = product).update(count = count)
                cart_items = CartItem.objects.order_by('product').filter(cart = cart)
                serializer = CartItemSerializer(cart_items, many = True)
                return created_response(serializer.data)
            return success_response({'error': 'no enough of this item in stock'})
        except Exception as error:
            return server_error({'error': f'something went wrong adding item to cart: {str(error)}'})


class RemoveItemView(APIView):
    def delete(self, request, format=None):
        user = request.user
        data = request.data

        try: product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error': 'the ID must be an integer'})

        try:
            cart = get_object_or_404(Cart, user=user)
            product = get_object_or_404(Product, id=product_id)

            if not cart._item_exists(product):
                return not_found({'error': 'El producto no está en tu carrito'})

            CartItem.objects.filter(cart=cart, product=product).delete()

            if not cart._item_exists(product):
                Cart.objects.filter(user=user).update( total_items =- 1 )

            cart_items = CartItem.objects.order_by('product').filter(cart=cart)
            serializer = CartItemSerializer(cart_items, many=True)
            return success_response(serializer.data)

        except Exception as error:
            return server_error({'result': 'error','message': f'{str(error)}'})


class EmptyCartView(APIView):
    def delete(self, request, format=None):
        try:
            cart = get_object_or_404( Cart, user = request.user )
            CartItem.objects.filter( cart = cart ).delete()
            cart.total_items = 0 
            cart.save()
            return success_response({'success':'cart empty successfully'})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class SynchCartView(APIView):
    def put(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            cart_items = data['cart_items']
            for cart_item in cart_items:
                cart = Cart.objects.filter(user = user)
                try:
                    product_id = int(cart_item['product_id'])
                except ValueError:
                    return bad_request({'error':'product id must be an integer'})
                
                cart_items = get_object_or_404(CartItem, cart = cart )
                product = get_object_or_404(Product, id = product_id)
                quantity = product.quantity

                if CartItem.objects.filter(cart = cart, product = product ).exists():
                    item = get_object_or_404(CartItem, cart = cart, product = product )
                    count = item.count
                    try:
                        # actualiza el item del carrito
                        cart_item_count = int(cart_item['count'])
                    except ValueError:
                        cart_item_count = 1
                    
                    # Chequeo con base de datos
                    if(cart_item_count + int(count)) <= int(quantity):
                        update_count = cart_item_count + int(count)
                        CartItem.objects.filter(cart = cart, product = product).update(count = update_count)
                else:
                    # agregar el item al carrito
                    try: cart_item_count = int(cart_item['count'])
                    except ValueError:
                        cart_item_count = 1
                    
                    if cart_item_count <= quantity:
                        CartItem.objects.create(cart = cart, product = product, count = cart_item_count)
                        if CartItem.objects.filter(cart = cart, product = product).exists():
                            Cart.objects.filter(cart = cart, product = product).update(total_items = int(cart_item['count']) + 1)
                
                return created_response({'success': 'cart Synchronized'})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {error}'})