from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    # djoser
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    # apps
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/products/', include('apps.product.urls')),
    path('api/shopping_cart/', include('apps.shopping_cart.urls')),
    path('api/shipping/', include('apps.shipping.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payment/', include('apps.payment.urls')),
    # path('api/profile/', include('user_profile.urls')),

    # re_path(r'^.*', TemplateView.as_view(template_name="index.html"))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
