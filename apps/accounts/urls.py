from django.urls import path

app_name='accounts'

urlpatterns = [
	path('get_items', GetItemsView.as_view()),
	path('add_item', AddItemView.as_view()),
	path('get_items_total', GetItemTotalView.as_view()),
	path('remove_item', RemoveItemView.as_view()),
	path('<int:productId>', views.GetReview.as_view()),
    path('new/<int:productId>', views.CreateReview.as_view()),
    path('review', views.UpdateReview.as_view()),
    path('del/<int:productId>', views.DeleteReview.as_view()),
    path('filter/<int:productId>', views.FilterReview.as_view()),
]