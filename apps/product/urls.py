from django.urls import path, re_path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name='product'

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('taxes', views.TaxViewSet)

urlpatterns = [
    path('categories', views.ListCategoriesView.as_view()),
    path('', views.ProductListView.as_view()),
    path('discounts', views.ListDiscountView.as_view()),
    path('detail/<int:id>', views.DetailProductView.as_view(), name="detail"),
    path('related/<int:productId>', views.ListRelatedView.as_view()),
    path('', include(router.urls))
]