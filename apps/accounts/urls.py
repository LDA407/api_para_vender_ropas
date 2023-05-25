from django.urls import path, re_path
from .views import *

app_name='accounts'

urlpatterns = [
	path('wishlist/get_items', GetItemsView.as_view()),
	path('wishlist/add_item', AddItemView.as_view()),
	path('wishlist/get_items_total', GetItemTotalView.as_view()),
	path('wishlist/remove_item', RemoveItemView.as_view()),
	path('reviews/<int:productId>', GetReview.as_view()),
    path('reviews/add/<int:productId>', CreateReview.as_view()),
    path('reviews/update/', UpdateReview.as_view()),
    path('reviews/delete/<int:productId>', DeleteReview.as_view()),
    path('reviews/filter/<int:productId>', FilterReview.as_view()),
]