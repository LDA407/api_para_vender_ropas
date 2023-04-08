from django.urls import path
from . import views

app_name='reviews'

urlpatterns = [
    path('<int:productId>', views.GetReview.as_view()),
    path('new/<int:productId>', views.CreateReview.as_view()),
    path('review', views.UpdateReview.as_view()),
    path('del/<int:productId>', views.DeleteReview.as_view()),
    path('filter/<int:productId>', views.FilterReview.as_view()),
]