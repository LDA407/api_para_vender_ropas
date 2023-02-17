import braintree
from rest_framework.views import APIView
from rest_framework import permissions
from django.http.response import HttpResponse, HttpResponseNotFound
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
# from django.db.models import Q
from cart.models import Cart, CartItem
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
		environment = settings.BT_ENVIRONMENT,
		merchant_id = settings.BT_MERCHANT,
		public_key = settings.BT_PUBLIC_KEY,
		private_key = settings.BT_PRIVATE_KEY
	)
)

class GenerateTokenView(APIView):
	def get(self, format= None):
		try:
			token = gateway.client_token.generate()
			return success_response({ 'braintree_token': token })
		except Exception as error:
			return server_error(
				{'error': f'something went wrong when retrieving orders: {error}'}
			)


class GetPaymentTotalView(APIView):

    def get(self, request, format=None):
        user = self.request.user
        # buscar igv en google, impuesto a la venta
        tax = 0.24
        shipping_id = str(request.query_params.get('shipping_id'))

        try:
            cart = Cart.objects.get(user=user)
            cart_items = get_list_or_404(CartItem, cart=cart)

            # Chequea si hay suficiente stock de cada producto en el carrito
            for cart_item in cart_items:
                product = get_object_or_404(Product, id=cart_item.product.id)
                if cart_item.product_not_available():
                    return not_found(
                        {'error': f'Not enough stock for product: {product.name}'},
                    )

            total_amount = sum([cart_item.raw_total_price() for cart_item in cart_items])
            total_compare_amount = sum([cart_item.raw_total_compare_price() for cart_item in cart_items])

            # Cupones
            # =======

            total_compare_amount = round(total_compare_amount, 2)
            original_price = round(total_amount, 2)
            estimated_tax = round(total_amount * tax, 2)
            total_amount += (total_amount * tax)

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
                'original_price': f'{original_price:.2f}',
                'total_amount': f'{total_amount:.2f}',
                'total_compare_amount': f'{total_compare_amount:.2f}',
                'estimated_tax': f'{estimated_tax:.2f}',
                'shipping_cost': f'{shipping_cost:.2f}',
            })
		
        except Cart.DoesNotExist:
            return not_found({'error': 'User has no cart'})

        except Shipping.DoesNotExist:
			return not_found({'error': 'Invalid shipping ID'})

        except Exception:
            return server_error(
                {'error': 'Something went wrong when retrieving orders'},
            )

decorators = [http.require_http_methods(["POST"])]
@method_decorator(decorators, name='dispatch')
class ProcessPaymentView(APIView):
	permission_classes = (permissions.IsAuthenticated)
	_CARTS = Cart.objects.all()
	_PRODUCTS = Product.objects.all()

	def post(self, request, format= None):
		user			= request.user
		data			= request.data
		tax				= 0.24
		nonce			= data.get('nonce')
		shipping_id		= str(data.get('shipping_id'))
		full_name		= data.get('full_name')
		address_line_1	= data.get('address_line_1')
		address_line_2	= data.get('address_line_2')
		city			= data.get('city')
		province		= data.get('province')
		zip_code		= data.get('zip_code')
		country			= data.get('country')
		telephone		= data.get('telephone')

		cart 			= Cart.objects.get(user = user)
		cart_items 		= get_object_or_404(CartItem, cart = cart)

		for cart_item in cart_items:
			get_object_or_404(self._PRODUCTS, id=cart_item.product.id)
			if cart_item.product_not_available():
				return HttpResponseNotFound("Error! Not enough item in stock")
			total_amount = cart_item.raw_total_price()
			
		# total_amount =  sum([[item.raw_total_price()] for item in cart_items])
		
		# cupones
		# =======

		total_amount += (total_amount * tax)
		shipping 		= get_object_or_404(self._PRODUCTS, id=int(shipping_id))
		shipping_name 	= shipping.name
		shipping_time 	= shipping.time_to_delivery
		shipping_price	= shipping.price

		total_amount += float(shipping_price)
		total_amount = round(total_amount, 2)

		try:
			# conectamos con braintree y le pasamos los datos de la compra
			new_transaction = gateway.Transaction.sale(
				{
					'amount': str(total_amount),
					'payment_method_nonce': str(nonce['nonce']),
					'options': {
						'submit_for_settlement': True,
					}
				}
			)
		except:
			return server_error({'error': 'Error processing the transaction'})
		
		if new_transaction.is_success or new_transaction.transaction:
			for cart_item in cart_items:
				update_product = self._PRODUCTS.get(id=cart_item.product.id)
				# actualiza la cantidad de productos en stok
				self._PRODUCTS.filter(id=cart_item.product.id).update(
					quantity = (int(update_product.quantity) - int(cart_item.count)),
					sold = (int(update_product.sold) + int(cart_item.count))
				)
			try:
				order = Order.objects.add(
					user = user,
					transaction_id = new_transaction.transaction.id,
					amount = total_amount,
					full_name = full_name,
					address_line_1 = address_line_1,
					address_line_2 = address_line_2,
					city = city,
					province = province,
					zip_code = zip_code,
					country = country,
					telephone = telephone,
					shipping_name = shipping_name,
					shipping_time = shipping_time,
					shipping_price = float(shipping_price),
				)
			except:
				return server_error({'error': 'Transaction succeded but failed to create the order'})
			
			for cart_item in cart_items:
				product = self._PRODUCTS.get(id=cart_item.product.id)
				try:
					OrderItem.objects.add(
						product = product,
						order = order,
						name = product.name,
						price = cart_item.product.price,
						count = cart_item.count
					)
				except:
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
			except:
				return server_error(
					{'error': 'Transaction succeded and order successfull, but failed to send mail'}
				)
			
			try:
				CartItem.objects.filter(cart = cart).delete()
				self._CARTS.filter(user = user).update(total_items = 0)
			except: 
				return server_error(
					{'error': 'Transaction succeded and order successfull, but failed to send mail'}
				)
			return response_417(
				{'error': 'Transaction successfull and order created'}
			)
		return bad_request({'error': 'Transaction failed'})
