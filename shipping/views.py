from urllib import request
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Shipping
from .seriallizers import ShippingSerializer

# Create your views here.
class GetShippingView(APIView):
	permission_clases = (permissions.AllowAny, )

	def get(self, request, format=None):
		_SHIPPING = Shipping.objects
		if _SHIPPING.all().exists():
			shipping_options = _SHIPPING.order_by('price').all()
			shipping_options = ShippingSerializer(shipping_options, many=True)
			return Response(
				{'shipping_options': shipping_options.data},
				status = status.HTTP_200_OK
			)
		return Response(
				{'error': 'no shippings options available'},
				status = status.HTTP_404_NOT_FOUND
			)
