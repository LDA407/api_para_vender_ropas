from django.urls import path
from .views import *

app_name='wishlist'

urlpatterns = [
	path('get_items', GetItemsView.as_view()),
	path('add_item', AddItemView.as_view()),
	path('get_items_total', GetItemTotalView.as_view()),
	path('remove_item', RemoveItemView.as_view()),
]