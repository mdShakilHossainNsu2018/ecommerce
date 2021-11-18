from django.urls import path
from .views import (
    ProductListView,
    ProductDetailSlugView,
    ProductDownloadView, CategoryDetailSlugView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='detail'),
    path('category/<slug:slug>/', CategoryDetailSlugView.as_view(), name='category'),
    path('<slug:slug>/<int:pk>/', ProductDownloadView.as_view(), name='download'),
]

