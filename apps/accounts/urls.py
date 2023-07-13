from django.urls import path, re_path
from .views import *
# from rest_framework import routers

# router = routers.SimpleRouter()
# router.register(r'wishlist', WishListItemCreateView, basename='wishlist')
# print(router.urls)
# router.register(r'accounts', AccountViewSet)
# urlpatterns = router.urls
app_name='accounts'

urlpatterns = [
	path('wishlist', WishListItemCreateView.as_view()),
	re_path(r'^wishlist/delete/(?P<id>[^/]+)/$', WishListItemDestroyView.as_view()),
	re_path(r'reviews$', ReviewListCreateView.as_view()),
    re_path(r'^reviews/updateOrDelete/(?P<id>[^/]+)/$', ReviewRetrieveUpdateDestroyView.as_view()),
    re_path(r'^reviews/filter/(?P<productId>[^/]+)/$', FilterReview.as_view()),
]