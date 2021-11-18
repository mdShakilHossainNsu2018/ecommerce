from django.urls import path

from .views import (
        OrderListView, 
        OrderDetailView,
        VerifyOwnership
        )

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('endpoint/verify/ownership/', VerifyOwnership.as_view(), name='verify-ownership'),
    path('<order_id>/', OrderDetailView.as_view(), name='detail'),
]