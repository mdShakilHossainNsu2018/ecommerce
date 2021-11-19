import json
from importlib import import_module
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressCheckoutForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order, ORDER_STATUS_CHOICES
from products.models import Product
from .models import Cart

import stripe

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_cu1lQmcg1OLffhLvYrSCp5XE")
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", 'pk_test_PrV61avxnHaWIYZEeiYTTVMZ')
stripe.api_key = STRIPE_SECRET_KEY


def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        "id": x.id,
        "url": x.get_absolute_url(),
        "name": x.name,
        "price": x.price
    }
        for x in cart_obj.products.all()]
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)


def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {"cart": cart_obj})


def cart_update(request):
    product_id = request.POST.get('product_id')

    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Show message to user, product is gone?")
            return redirect("cart:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)  # cart_obj.products.add(product_id)
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        # return redirect(product_obj.get_absolute_url())
        if request.is_ajax():  # Asynchronous JavaScript And XML / JSON
            print("Ajax request")
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_obj.products.count()
            }
            return JsonResponse(json_data, status=200)  # HttpResponse
            # return JsonResponse({"message": "Error 400"}, status=400) # Django Rest Framework
    return redirect("cart:home")


def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_required = not cart_obj.is_digital
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card

    if request.method == "POST":
        "check that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()  # sort a signal for us
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    '''
                    is this the best spot?
                    '''
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")
            else:
                print(crg_msg)
                return redirect("cart:checkout")
    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        "shipping_address_required": shipping_address_required,
    }
    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})


def others_checkout(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_required = not cart_obj.is_digital
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "shipping_address_required": shipping_address_required,
    }
    return render(request, "carts/others-payment.html", context)


# @login_required(login_url="login/")
def ssl_save(request):
    # print(request.POST.get("order"))
    url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    post_body = {}
    order_id = request.POST.get("order", None)
    order = Order.objects.get(order_id=order_id)
    if request.method == "POST" and order:
        data = request.POST
        post_body['store_id'] = settings.STORE_ID
        post_body['store_passwd'] = settings.STORE_PASS
        post_body['total_amount'] = str(order.total)
        post_body['currency'] = "BDT"
        post_body['tran_id'] = str(order.order_id)
        post_body['product_category'] = "Online"
        post_body['success_url'] = settings.BASE_URL + reverse("cart:ssl_success", kwargs={'order_id': order_id,
                                                                                           'session_key': request.session.session_key})
        post_body['fail_url'] = settings.BASE_URL + reverse("cart:ssl_fail", kwargs={'order_id': order_id,
                                                                                     'session_key': request.session.session_key})
        post_body['cancel_url'] = settings.BASE_URL + reverse("cart:ssl_fail",
                                                              kwargs={'order_id': order_id, 'session_key':
                                                                  request.session.session_key})
        post_body['emi_option'] = 0
        post_body['cus_name'] = "Any one"
        post_body['cus_email'] = request.user.email
        post_body['cus_add1'] = order.billing_address.address_line_1
        post_body['cus_add2'] = order.billing_address.address_line_2
        post_body['cus_city'] = order.billing_address.city
        post_body['cus_state'] = order.billing_address.state
        post_body['cus_postcode'] = order.billing_address.postal_code
        post_body['cus_country'] = order.billing_address.country
        post_body['cus_phone'] = "01711111111"
        post_body['shipping_method'] = "NO"
        post_body['num_of_item'] = 1
        post_body['product_name'] = "Unknown"
        post_body['product_profile'] = "general"
        response = requests.post(url=url, data=post_body)

        if response.status_code == 200 and json.loads(response.text)["status"] == "SUCCESS":
            # print("sucess on api hit")
            print(response.text)
            return HttpResponseRedirect(json.loads(response.text)["GatewayPageURL"])

    return redirect("cart:home")


@csrf_exempt
def ssl_success(request, order_id, session_key):
    request.session = SessionStore(session_key=session_key)
    order_obj = Order.objects.get(order_id=order_id)
    is_prepared = order_obj.check_done()
    if is_prepared:
        order_obj.mark_paid()  # sort a signal for us
        try:
            request.session["cart_items"] = 0
            del request.session["cart_id"]
        except KeyError:
            print("Key error")
    return redirect("cart:success")


@csrf_exempt
def ssl_fail(request, order_id, session_key):
    request.session = SessionStore(session_key=session_key)
    return render(request, "carts/fail.html", {})

# def ssl_get_start_session(request):
#     url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
#
#     # sslcz = SSLCOMMERZ(ssl_settings)
#     post_body = {}
#     #
#     # post_body['store_id'] = ssl_settings["store_id"]
#     # post_body['store_passwd'] = ssl_settings["store_pass"]
#     post_body['total_amount'] = "100"
#     post_body['currency'] = "REF123"
#     post_body['tran_id'] = "12345"
#     post_body['success_url'] = "http://yoursite.com/success.php"
#     post_body['fail_url'] = "http://yoursite.com/fail.php"
#     post_body['cancel_url'] = "http://yoursite.com/cancel.php"
#     post_body['emi_option'] = 0
#     post_body['cus_name'] = "test"
#     post_body['cus_email'] = "test@test.com"
#     post_body['cus_phone'] = "01711111111"
#     post_body['cus_fax'] = "01711111111"
#     post_body['cus_add1'] = "customer address"
#     post_body['cus_add2'] = "customer address"
#     post_body['cus_city'] = "Dhaka"
#     post_body['cus_state'] = "Dhaka"
#     post_body['cus_postcode'] = "1234"
#     post_body['cus_country'] = "Bangladesh"
#     post_body['shipping_method'] = "NO"
#     post_body['ship_name'] = "NO ds"
#     post_body['ship_add1'] = "NO ds"
#     post_body['ship_add2'] = "NO ds"
#     post_body['ship_city'] = "Dhaka"
#     post_body['ship_state'] = "Dhaka"
#     post_body['ship_postcode'] = "1223"
#     post_body['ship_country'] = "Bangladesh"
#     post_body['multi_card_name'] = ""
#     post_body['num_of_item'] = 1
#     post_body['product_name'] = "Test"
#     post_body['product_category'] = "Test Category"
#     post_body['product_profile'] = "general"
#     response = requests.post(url=url, data=post_body)
#     # response = sslcz.createSession(post_body)  # API response
#     print(response)
