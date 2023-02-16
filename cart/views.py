from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.http.response import HttpResponse,JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.forms.models import model_to_dict
from .models import Cart, CartItem
from product.models import Product
from product.serializers import ProductSerializer
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


class GetItemsView(APIView):
	def get(self, request):
		user = self.request.user
		try:
			cart = Cart.objects.get( user = user )
			cart_items = CartItem.objects.order_by('product').filter( cart = cart)
			result = []

			if CartItem.objects.filter( cart = cart ).exists():
				for item in cart_items:
					product = Product.objects.get(id = item.product.id)
					product = ProductSerializer(product)
					result.append(
						{
							'id': item.id,
							'count': item.count,
							'product': product.data,
						}
					)
			return Response( {'cart': result}, status=status.HTTP_200_OK )
		except:
			return Response(
				{'Error': 'algo ocurrio en el camino...'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class AddItemView(APIView):

	# def dispatch(self, request, *args, **kwargs):
	# 	_META = self.request.META
	# 	if 'USE_X_FORWARDED_HOST' in _META:
	# 		print("USE_X_FORWARDED_HOST estaa en los cabeceros")
	# 		# self.request.is_secure == True
	# 		return _META['USE_X_FORWARDED_HOST'] == 'on'
	# 	if not self.request.is_secure():
	# 		return HttpResponse(
	# 			"Insecure request, please upgrade to https",
	# 			status=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED
	# 		)
	# 	if not 'HTTP_AUTHORIZATION' in _META:
	# 		return HttpResponse( status=status.HTTP_401_UNAUTHORIZED )

	# 	return super().dispatch(request, *args, **kwargs)

	def post(self, request):
		user = self.request.user
		data = self.request.data
		count = 1

		try:
			product_id = int(data['product_id'])
		except:
			return Response(
				{'error':'product id must be an integer'},
				status=status.HTTP_404_NOT_FOUND
			)
		
		try:
			# verifica si el producto existe
			cart = Cart.objects.get(user = user)
			if not Product.objects.filter(id = product_id).exists():
				return HttpResponseNotFound(
					f'the product with id {product_id} does not exists')
				# return Response(
				# 	{'error':f'the product with id {product_id} does not exists'},
				# 	status=status.HTTP_404_NOT_FOUND
				# )
			
			product = get_object_or_404( Product, id = product_id )


			if CartItem.objects.filter(cart = cart, product = product).exists():
				return Response(
					{'error':'the product already in cart'},
					status=status.HTTP_409_CONFLICT
				)
			
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
						result.append(
							{
								'id': item.id,
								'count': item.count,
								'product': product.data,
							}
						)
					return Response(
						{'cart': result},
						status=status.HTTP_201_CREATED
					)
				return Response(
					{'error': 'no enough of this item in stock'},
					status=status.HTTP_200_OK
				)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class GetTotalView(APIView):
	def get(self, request):
		user = self.request.user

		try:
			cart =  Cart.objects.get( user = user )
			cart_items = get_list_or_404(CartItem, cart = cart )
			costo_total = 0.0
			total_con_descuentos = 0.0
			
			for cart_item in cart_items:
				costo_total += cart_item.raw_total_price()
				total_con_descuentos += cart_item.raw_total_compare_price()

			costo_total = round(costo_total, 2)
			total_con_descuentos = round(total_con_descuentos, 2)
			# ====================
			
			return Response(
				{
					'costo_total': costo_total,
					'total_con_descuentos': total_con_descuentos
				},
				status=status.HTTP_200_OK
			)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class GetItemTotalView(APIView):

	# def dispatch(self, request, *args, **kwargs):
	# 	_META = self.request.META
	# 	if 'USE_X_FORWARDED_HOST' in _META:
	# 		print("USE_X_FORWARDED_HOST estaa en los cabeceros")
	# 		# self.request.is_secure == True
	# 		return _META['USE_X_FORWARDED_HOST'] == 'on'
	# 	# if not self.request.is_secure():
	# 	# 	return HttpResponse(
	# 	# 		"Insecure request, please upgrade to https",
	# 	# 		status=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED
	# 	# 	)
	# 	if not 'HTTP_AUTHORIZATION' in _META:
	# 		return HttpResponse(
	# 			"Error! User not provider credentials",
	# 			status=status.HTTP_401_UNAUTHORIZED
	# 		)
	# 	return super().dispatch(request, *args, **kwargs)

	def get(self, request):
		user = self.request.user

		try:
			cart =  Cart.objects.get( user = user )
			total_items = cart.total_items
			return Response(
				{'total_items': total_items}, status=status.HTTP_200_OK
			)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class UpdateItemView(APIView):
	def put(self, request, format=None):
		user = self.request.user
		data = self.request.data
		try:
			product_id = int(data['product_id'])
		except:
			return Response(
				{'error':'product id must be an integer'},
				status=status.HTTP_404_NOT_FOUND
			)
		
		try:
			count = int(data['count'])
		except:
			return Response(
				{'error':'count id must be an integer'},
				status=status.HTTP_404_NOT_FOUND
			)
		
		try:
			product = get_object_or_404( Product, id = product_id )
			cart =  Cart.objects.get( user = user )
			if not CartItem.objects.filter(
				cart = cart,
				product = product
			).exists():
				return Response(
					{'error':'El producto no esta en tu carrito'},
					status=status.HTTP_404_NOT_FOUND
				)

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
					result.append(
						{
							'id': item.id,
							'count': item.count,
							'product': product.data,
						}
					)
				return Response(
					{'cart': result},
					status=status.HTTP_201_CREATED
				)
			return Response(
				{'error': 'no enough of this item in stock'},
				status=status.HTTP_200_OK
			)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class RemoveItemView(APIView):
	def delete(self, request, format=None):
		user = self.request.user
		data = self.request.data

		try:
			product_id = int(data['product_id'])
		except:
			return Response(
				{'error':'product id must be an integer'},
				status=status.HTTP_404_NOT_FOUND
			)
		
		try:
			product = get_object_or_404(Product, id = product_id )
			cart =  Cart.objects.get( user = user )
			if not CartItem.objects.filter(
				cart = cart,
				product = product
			).exists():
				return Response(
					{'error':'El producto no esta en tu carrito'},
					status=status.HTTP_404_NOT_FOUND
				)
			else:
				# si existe se elimina
				CartItem.objects.filter(
					cart = cart,
					product = product
				).delete()

			if not CartItem.objects.filter(
				cart = cart,
				product = product
			).exists():
				CartItem.objects.filter(
					cart = cart,
					product = product
				).update( total_items = int(cart.count) - 1 )
				
				cart_items = CartItem.objects.order_by('product').filter(cart = cart)
				result = []
				for item in cart_items:
					product = Product.objects.get(id = item.product.id)
					product = ProductSerializer(product)
					result.append(
						{
							'id': item.id,
							'count': item.count,
							'product': product.data,
						}
					)
				return Response(
					{'cart': result},
					status=status.HTTP_201_CREATED
				)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class EmptyCartView(APIView):
	def delete(self, request, format=None):
		user = self.request.user
		# data = self.request.data

		try:
			cart = Cart.objects.get(user = user )
			get_object_or_404(CartItem, cart = cart).delete()
			Cart.objects.get( user = user ).update( total_items = 0 )
			return Response(
					{'success':'cart empty successfully'},
					status=status.HTTP_404_NOT_FOUND
				)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


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
				except:
					return Response(
						{'error':'product id must be an integer'},
						status=status.HTTP_404_NOT_FOUND
					)
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
					except:
						cart_item_count = 1
					
					# Chequeo con base de datos
					if(cart_item_count + int(count)) <= int(quantity):
						update_count = cart_item_count + int(count)
						CartItem.objects.filter(
							cart = cart, product = product
						).update(count = update_count)
				else:
					# agregar el item al carrito
					try:
						cart_item_count = int(cart_item['count'])
					except:
						cart_item_count = 1
					
					if cart_item_count <= quantity:
						CartItem.object.create(
							product = product, cart = cart, count = cart_item_count
						)
						if CartItem.object.filter( product = product, cart = cart ).exists():
							
							Cart.object.filter(
								cart = cart, product = product
							).update(
								total_items = int(cart_item['count']) + 1
							)
				return Response(
					{'success': 'cart Synchronized'},
					status=status.HTTP_201_CREATED
				)
		except:
			return Response(
				{'error': 'something went wrong adding intem to cart'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)