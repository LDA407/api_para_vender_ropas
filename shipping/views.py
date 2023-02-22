
from rest_framework.views import APIView
from rest_framework import permissions
from utils.responses import success_response, not_found
from .models import Shipping
from .seriallizers import ShippingSerializer

# Create your views here.
class GetShippingView(APIView):
    permission_clases = (permissions.AllowAny, )
    _SHIPPING = Shipping.objects.all()

    def get(self, format=None):
        if self._SHIPPING.exists():
            shipping_options = self._SHIPPING.order_by('price').all()
            shipping_options = ShippingSerializer(shipping_options, many=True)
            return success_response({'shipping_options': shipping_options.data})
        return not_found({'error': 'no shippings options available'})