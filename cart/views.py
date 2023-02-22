from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from .models import Cart, CartItem
from product.models import Product
from product.serializers import ProductSerializer
from utils.responses import *


class GetItemsView(APIView):
    def get(self, request):
        user = request.user
        try:
            cart = get_object_or_404(Cart, user=user)
            cart_items = cart.cartitem_set.select_related('product').order_by('product')
            result = []

            for item in cart_items:
                serializer = ProductSerializer(item.product)
                result.append({
                    'id': item.id,
                    'count': item.count,
                    'product': serializer.data
                })
            return success_response({'cart': result})
        except Cart.DoesNotExist:
            return not_found({'Error': 'El carrito no existe'})
        except Exception as error:
            return server_error({'Error': f'{str(error)}'})


class AddItemView(APIView):

    def post(self, request):
        user = request.user
        data = request.data
        count = 1
        print(data)
        
        try: product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error': 'product id must be an integer'})
        try:
            cart = Cart.objects.get(user = user)
            product = get_object_or_404( Product, id = int(product_id) )

            if CartItem.objects.filter(cart = cart, product = product).exists():
                return conflict_response({'error':'the product already in cart'})

            if int(product.quantity) > 0:
                CartItem.objects.create(
                    product = product,
                    cart = cart,
                    count = count
                )
                # si el producto ya existe le suma 1
                if CartItem.objects.filter(cart = cart, product = product).exists():
                    Cart.objects.filter(user = user).update(
                        total_items = int(cart.total_items) + 1
                    )
                    cart_items = CartItem.objects.order_by(
                        'product'
                    ).filter(cart = cart)

                    result = []
                    for item in cart_items:
                        product = Product.objects.get(id = item.product.id)
                        product = ProductSerializer(product)
                        result.append({
                            'id': item.id,
                            'count': item.count,
                            'product': product.data,
                        })
                return created_response({'cart': result})
            return success_response({'error': 'no enough of this item in stock'})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class GetTotalView(APIView):
    def get(self, request):
        user = self.request.user

        try:
            cart = Cart.objects.get(user=user)
            # cart_items = CartItem.objects.filter(cart=cart)
            costo_total = cart.get_total_amount()
            # total_compare_amount = cart.get_total_compare_amount()

            return success_response({
                'costo_total': costo_total,
                # 'total_con_descuentos': total_compare_amount
            })

        except Cart.DoesNotExist:
            return not_found({'error': 'User cart not found'})

        except Exception as error:
            return server_error({'error': f'Something went wrong: {str(error)}'})


class GetItemTotalView(APIView):

    def get(self, request):
        user = request.user

        try:
            cart =  Cart.objects.get( user = user )
            total_items = cart.total_items
            return success_response({'total_items': total_items})
        except Exception as error:
            return server_error({'error': f'something went wrong adding intem to cart: {str(error)}'})


class UpdateItemView(APIView):
    def put(self, request, format=None):
        user = request.user
        data = request.data

        try:
            product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error':'product id must be an integer'})

        try:
            count = int(data.get('count'))
        except ValueError:
            return bad_request({'error':'count id must be an integer'})
        
        try:
            product = get_object_or_404( Product, id = product_id )
            cart =  Cart.objects.get( user = user )
            if not CartItem.objects.filter(cart = cart, product = product).exists():
                return not_found({'error':'El producto no esta en tu carrito'})

            if count <= product.quantity:
                CartItem.objects.filter(
                    cart = cart,
                    product = product
                ).update(count=count)

                cart_items = CartItem.objects.order_by('product').filter(cart=cart)
                result = []
                for item in cart_items:
                    product = Product.objects.get(id = item.product.id)
                    product = ProductSerializer(product)
                    result.append({
                        'id': item.id,
                        'count': item.count,
                        'product': product.data
                    })
                return created_response({'cart': result})
            return success_response({'error': 'no enough of this item in stock'})
        except Exception as error:
            return server_error({'error': f'something went wrong adding item to cart: {str(error)}'})


class RemoveItemView(APIView):
    def delete(self, request, format=None):
        user = request.user
        data = request.data

        try:
            product_id = int(data.get('product_id'))
        except ValueError:
            return bad_request({'error': 'El id del producto debe ser un entero'})

        try:
            product = get_object_or_404(Product, id=product_id)
            cart = Cart.objects.get(user=user)
            if not CartItem.objects.filter(cart=cart, product=product).exists():
                return not_found({'error': 'El producto no está en tu carrito'})
            CartItem.objects.filter(cart=cart, product=product).delete()

            # Se actualiza el conteo de elementos y se devuelve la lista actualizada del carrito
            CartItem.objects.filter(cart=cart, product=product).update(total_items=int(cart.count) - 1)
            cart_items = CartItem.objects.order_by('product').filter(cart=cart)
            result = []
            for item in cart_items:
                product = Product.objects.get(id=item.product.id)
                product_serializer = ProductSerializer(product)
                result.append({
                    'id': item.id,
                    'count': item.count,
                    'product': product_serializer.data,
                })
            return success_response({'cart': result})
        except Exception as error:
            return server_error({'error': 'Algo salió mal al eliminar el elemento del carrito'})


class EmptyCartView(APIView):
    def delete(self, request, format=None):
        user = request.user
        # data = self.request.data

        try:
            cart = Cart.objects.get(user = user )
            cart_item = get_list_or_404(CartItem, cart = cart)
            cart_item.delete()
            Cart.objects.get( user = user ).update( total_items = 0 )
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
                
                cart = get_object_or_404(CartItem, cart = cart )
                product = Product.objects.get(id = product_id)
                quantity = product.quantity

                if CartItem.objects.filter(
                    cart = cart,
                    product = product
                ).exists():
                    item = CartItem.objects.get(
                        cart = cart,
                        product = product
                    )
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
                        CartItem.object.create(product = product, cart = cart, count = cart_item_count)
                        if CartItem.object.filter( product = product, cart = cart ).exists():
                            Cart.object.filter(cart = cart, product = product).update(total_items = int(cart_item['count']) + 1)
                return created_response({'success': 'cart Synchronized'})
        except:
            return server_error({'error': 'something went wrong adding intem to cart'})