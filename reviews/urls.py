from django.urls import path

from reviews.views import create_review_view, thanks

app_name = "reviews"
urlpatterns = [
    path('create/<int:product_id>/', create_review_view, name='create'),
    path('thanks/', thanks, name='thanks'),
]