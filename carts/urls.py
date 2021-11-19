from django.urls import path

from .views import (
    cart_home,
    cart_update,
    checkout_home,
    checkout_done_view, others_checkout, ssl_save, ssl_success, ssl_fail
)

urlpatterns = [
    path('', cart_home, name='home'),
    path('checkout/success/', checkout_done_view, name='success'),
    path('checkout/', checkout_home, name='checkout'),
    path('checkout/others/', others_checkout, name='others-checkout'),
    path('checkout/others/ssl/', ssl_save, name='ssl_save'),
    path('checkout/others/ssl/success/<order_id>/<session_key>/', ssl_success, name='ssl_success'),
    path('checkout/others/ssl/fail/<order_id>/<session_key>/', ssl_fail, name='ssl_fail'),
    path('update/', cart_update, name='update'),
]
