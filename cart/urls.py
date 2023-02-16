from django.urls import path
from .views import (
	GetItemsView,
	AddItemView,
	GetTotalView,
	GetItemTotalView,
	UpdateItemView,
	RemoveItemView,
	EmptyCartView,
	SynchCartView
)

app_name='cart'
urlpatterns = [
	path('get_items', GetItemsView.as_view()),
	path('add_item', AddItemView.as_view()),
	path('get_total', GetTotalView.as_view()),
	path('get_items_total', GetItemTotalView.as_view()),
	path('update_item', UpdateItemView.as_view()),
	path('remove_item', RemoveItemView.as_view()),
	path('empty_cart', EmptyCartView.as_view()),
	path('synch_cart', SynchCartView.as_view())
]