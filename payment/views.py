import braintree
from rest_framework.views import APIView
from rest_framework import permissions
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
# from django.db.models import Q
from cart.models import Cart, CartItem
from coupons.models import FixedPriceCoupon, PorcentageCoupon
from orders.models import Order, OrderItem
from product.models import Product
from shipping.models import Shipping


from django.views.decorators import csrf, http
from django.utils.decorators import method_decorator
from utils.responses import *

# def catalog(request):
# site_name = "Modern Musician"
# response_html = u"<html><body>Welcome to %s.</body></html>" % site_name
# return HttpResponse(response_html)

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.BT_MERCHANT_ID,
        public_key=settings.BT_PUBLIC_KEY,
        private_key=settings.BT_PRIVATE_KEY
    )
)


class GenerateTokenView(APIView):
    def get(self, format= None):
        try:
            # pass client_token to your front-end
            # client_token = gateway.client_token.generate({
            #     "customer_id": a_customer_id
            # })
            token = gateway.client_token.generate()
            return success_response({ 'braintree_token': token })
        except Exception as error:
            return server_error(
                {'error': f'something went wrong when retrieving orders: {error}'}
            )


class GetPaymentTotalView(APIView):

    # def dispatch(self, request, *args, **kwargs):
    #     if 'HTTP_X_FORWARDED_PROTO' in self.request.META and self.request.META['HTTP_X_FORWARDED_PROTO'] == 'https':
    #         self.request.is_secure = lambda: True

    #     if not self.request.is_secure():
    #         return not_suported_response("Insecure request. Please upgrade to HTTPS")

    #     if 'HTTP_AUTHORIZATION' not in self.request.META:
    #         return unauthorized_response("Error! User not provided credentials")

    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        user = self.request.user
        tax = 0.24
        shipping_id = str(request.query_params.get('shipping_id'))
        coupon_name = request.query_params.get('coupon_name')

        try:
            cart = Cart.objects.get(user=user)
            cart_items = cart.cartitem_set.all()

            # Chequea si hay suficiente stock de cada producto en el carrito
            for cart_item in cart_items:
                not_available = cart_item.product_not_available()
                if not_available:
                    return not_found(f"Error! Not enough stock for product: {str(not_available)}")

            total_amount = cart.get_total_amount()
            total_compare_amount = cart.get_total_compare_amount()

            original_price = total_amount
            # estimated_tax = round(total_amount * tax, 2)
            total_amount += (total_amount * tax)

            # Coupon
            # =====
            if coupon_name != "":
                if FixedPriceCoupon.objects.filter(name__iexact = coupon_name).exists():
                    fixed_price_coupon = FixedPriceCoupon.objects.get(name=coupon_name)
                    discount_amount = float(fixed_price_coupon.discount_amount)
                    if discount_amount < total_amount:
                        total_amount -= discount_amount
                        total_after_coupon = total_amount
                
                elif PorcentageCoupon.objects.filter(name_iexact = coupon_name).exists():
                    percentage_coupon = PorcentageCoupon.objects.get(name=coupon_name)
                    discount_percentage = float(percentage_coupon)

                    if discount_amount > 1 and discount_amount < 100:
                        total_amount -= (total_amount * discount_amount / 100)
                        total_after_coupon = total_amount
            
            total_after_coupon = round(total_after_coupon, 2)
            # Envío
            # =====
            shipping_cost = 0.0
            shipping = get_object_or_404(Shipping, id=shipping_id)
            if shipping:
                # Se le suma el costo de envío
                shipping_cost = shipping.price
                total_amount += shipping_cost

            total_amount = round(total_amount, 2)

            return success_response({
                'original_price'        : f'{original_price:.2f}',
                'total_after_coupon'    : f'{total_after_coupon:.2f}',
                'total_amount'          : f'{total_amount:.2f}',
                'total_compare_amount'  : f'{total_compare_amount:.2f}',
                # 'estimated_tax'         : f'{estimated_tax:.2f}',
                'shipping_cost'         : f'{shipping_cost:.2f}',
            })
        
        except (Cart.DoesNotExist, Shipping.DoesNotExist) as error:
            return not_found(f"Error the object does not exist: {str(error)}")

        except Exception as error:
            return server_error(
                f"Something went wrong when retrieving orders: {str(error)}")


decorators = [http.require_http_methods(["POST"])]
@method_decorator(decorators, name='dispatch')
class ProcessPaymentView(APIView):
    permission_classes = (permissions.IsAuthenticated)

    # def dispatch(self, request, *args, **kwargs):
    #     if 'HTTP_X_FORWARDED_PROTO' in self.request.META and self.request.META['HTTP_X_FORWARDED_PROTO'] == 'https':
    #         self.request.is_secure = lambda: True

    #     if not self.request.is_secure():
    #         return not_suported_response("Insecure request. Please upgrade to HTTPS")

    #     if 'HTTP_AUTHORIZATION' not in self.request.META:
    #         return unauthorized_response("Error! User not provided credentials")

    #     return super().dispatch(request, *args, **kwargs)

    def post(self, request, format= None):
        _CARTS = Cart.objects.all()
        _PRODUCTS = Product.objects.all()
        _CART_ITEMS = CartItem.objects.all()
        
        user			= request.user
        data			= request.data
        tax				= 0.24
        nonce			= data.get('nonce')
        coupon_name	    = str(data.get('coupon_name'))
        shipping_id		= str(data.get('shipping_id'))
        full_name		= data.get('full_name')
        address_line_1	= data.get('address_line_1')
        address_line_2	= data.get('address_line_2')
        city			= data.get('city')
        province		= data.get('province')
        zip_code		= data.get('zip_code')
        country			= data.get('country')
        telephone		= data.get('telephone')

        cart 			= _CARTS.filter(user = user)
        cart_items      = _CART_ITEMS.filter(cart=cart).first()

        for cart_item in cart_items:
            not_available = cart_item.product_not_available()
            if not_available:
                return not_found(f"Error! Not enough stock for product: {str(not_available)}")
        
        # Coupon
        # =====
        if coupon_name != "":
            if FixedPriceCoupon.objects.filter(name__iexact = coupon_name).exists():
                fixed_price_coupon = FixedPriceCoupon.objects.get(name=coupon_name)
                discount_amount = float(fixed_price_coupon.discount_amount)
                if discount_amount < total_amount:
                    total_amount -= discount_amount
            
            elif PorcentageCoupon.objects.filter(name_iexact = coupon_name).exists():
                percentage_coupon = PorcentageCoupon.objects.get(name=coupon_name)
                discount_percentage = float(percentage_coupon)
                if discount_amount > 1 and discount_amount < 100:
                    total_amount -= (total_amount * discount_amount / 100)
        

        total_amount += (total_amount * tax)
        shipping 		= get_object_or_404(_PRODUCTS, id=shipping_id)
        shipping_name 	= shipping.name
        shipping_time 	= shipping.time_to_delivery
        shipping_price	= shipping.price

        total_amount += float(shipping_price)
        total_amount = round(total_amount, 2)

        try:
            # conectamos con braintree y le pasamos los datos de la compra
            new_transaction = gateway.transaction.sale({
                'amount': str(total_amount),
                'payment_method_nonce': str(nonce['nonce']),
                'options': {
                    'submit_for_settlement': True,
                }
            })
        except Exception as error:
            return server_error(f"Error processing the transaction: {str(error)}")
        
        if new_transaction.is_success or new_transaction.transaction:
            from django.db.models import F
            for cart_item in cart_items:
                # actualiza la cantidad de productos en stok
                _PRODUCTS.filter(id=cart_item.product.id).update(
                    quantity = F('quantity') - cart_item.count,
                    sold = F('sold') + cart_item.count
                )
            try:
                order = Order.objects.add(
                    user              = user,
                    transaction_id    = new_transaction.transaction.id,
                    amount            = total_amount,
                    full_name         = full_name,
                    address_line_1    = address_line_1,
                    address_line_2    = address_line_2,
                    city              = city,
                    province          = province,
                    zip_code          = zip_code,
                    country           = country,
                    telephone         = telephone,
                    shipping_name     = shipping_name,
                    shipping_time     = shipping_time,
                    shipping_price    = float(shipping_price)
                )
            except Exception as error:
                return server_error(f"Error! The transaction succeded but failed to create the order: {str(error)}")
            
            for cart_item in cart_items:
                product = _PRODUCTS[cart_item.product.id]
                try:
                    OrderItem.objects.add(
                        product = product,
                        order = order,
                        name = product.name,
                        price = product.price,
                        count = cart_item.count
                    )
                except Exception as error:
                    return server_error(
                        {'error': 'Transaction succeded and order created, but failed to create the order'}
                    )
            
            try:
                send_mail(
                    'You order details',
                    f'Hey {full_name},'
                    +'\n\nWe recieved your order!'
                    +'\n\nGive us some time to procces your order and ship it out to you.' 
                    +'\n\nYou can go on your user dashboar to check the status of your order.' 
                    +'\n\nSincerely' 
                    +'\nShop Time' ,
                    'mailloquesea@nimeimporta.com',
                    [user.mail],
                    fail_silently=False
                )
            except Exception as error:
                return server_error(
                    f"Transaction succeded and order successfull, but failed to send mail {str(error)}")
            
            try:
                CartItem.objects.filter(cart = cart).delete()
                cart_updated = _CARTS.filter(user = user).update(total_items = 0)
                cart_updated.save()
            except Exception as error:
                return server_error(
                    f"Transaction succeded and order successfull, but failed to eliminate {str(error)}"
                )
            return expectation_failed({'error': 'Transaction successfull and order created'})
        return bad_request({'error': 'Transaction failed'})
