from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters, generics, permissions, viewsets, mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from utils.responses import *

from .models import *
from .serializers import *

class BaseAttrsViewSet(
        viewsets.GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin
    ):
	# authentication_class = (TokenAuthentication,)
	permission_classes = (permissions.IsAuthenticated,)

	# def get_queryset(self):
	# 	return self.queryset.filter(user=self.request.user).order_by('-name')

	def perform_create(self, serializers):
		serializers.save()


class TagViewSet(BaseAttrsViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer


class TaxViewSet(BaseAttrsViewSet):
	queryset = Tax.objects.all()
	serializer_class = TaxSerializer


class ListCategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(parent = None)
    serializer_class = CategorySerializer


class ListDiscountView(generics.ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class =DiscountSerializer


class ProductListView(generics.ListAPIView):
    # renderer_classes = [JSONRenderer]
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date_created', 'sold', 'name']
    ordering = 'date_created'

    # def filter_queryset(self, queryset):
    #     return super().filter_queryset(queryset)

    def get_queryset(self):
        qs = super(ProductListView, self).get_queryset()
        price_range = self.request.query_params.get("price_range")
        # category_id = self.request.query_params.get("category_id")

        if price_range is not None:
            if price_range == "More then 80":
                return qs.filter(price__gte=80)
            else:
                val1, val2 = price_range.split("-")
                return qs.filter(price__range=[val1, val2])
        return qs


class DetailProductView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = "id"


class ListRelatedView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        id = self.kwargs["productId"]
            
        product = get_object_or_404(Product, id = id)
        queryset = Product.objects.filter(category = product.category).exclude(id = id).order_by('-sold')
        return queryset[:3]
