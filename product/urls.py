from django.urls import path
from . import views


app_name='product'


urlpatterns = [
    path('categories', views.ListCategoriesView.as_view()),
    path('list', views.ProductListView.as_view()),
    path('search', views.SearcherProduct.as_view()),
    path('search/filtered', views.FilterBySearchView.as_view()),
    path('detail/<int:productId>', views.DetailProductView.as_view()),
    path('related_products/<productId>', views.ListRelatedView.as_view()),
]