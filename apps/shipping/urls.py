from django.urls import path
from . import views
app_name='shipping'

urlpatterns = [
    path('shipping_options', views.GetShippingView.as_view()),
]