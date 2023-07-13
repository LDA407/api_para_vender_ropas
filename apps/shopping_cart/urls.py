from django.urls import path
from .views import *

app_name='shopping_cart'
urlpatterns = [
	path('get_items', GetItemsView.as_view()),
	path('add_item', AddItemView.as_view()),
	path('list-and-create', CartItemListCreate.as_view()),
	path('get_total', GetTotalView.as_view()),
	path('get_items_total', GetItemTotalView.as_view()),
	path('update_item', UpdateItemView.as_view()),
	path('remove_item', RemoveItemView.as_view()),
	path('empty_cart', EmptyCartView.as_view()),
	path('synch_cart', SynchCartView.as_view()),
	path('updateOrDelete/<int:id>', CartItemveUpdateDestroyView.as_view()),
]