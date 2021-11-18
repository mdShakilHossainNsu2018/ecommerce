# from django.views import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404, redirect
from orders.models import ProductPurchase
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
from .models import Product, ProductFile, Category


class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()


class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = "products/featured-detail.html"


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
        return views


class ProductListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, "products/list.html", context)


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        product_files = ProductFile.objects.all().filter(product=self.object)
        # print(product_files)
        context['cart'] = cart_obj
        context['product_files'] = product_files
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')

        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found..")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404("Uhhmmm ")
        return instance


class CategoryDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Category.objects.all()
    template_name = "products/category.html"

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailSlugView, self).get_context_data(*args, **kwargs)
        products = Product.objects.filter(category=self.object)

        # print(Product.objects.all().filter(category=context.object))
        # cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        # product_files = ProductFile.objects.all().filter(product=self.object)
        # print(product_files)
        context['products'] = products
        # context['product_files'] = product_files
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')

        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Category.objects.get(slug=slug)
            # instance = Product.objects.all().filter(category=category, active=True).first()
        except Category.DoesNotExist:
            raise Http404("Not found..")
        except Category.MultipleObjectsReturned:
            qs = Category.objects.filter(slug=slug)
            instance = qs.first()
        except:
            raise Http404("Uhhmmm ")
        return instance


class ProductDownloadView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
        if downloads_qs.count() != 1:
            raise Http404("Download not found")
        download_obj = downloads_qs.first()
        # permission checks

        can_download = False
        user_ready = True
        if download_obj.user_required:
            if not request.user.is_authenticated():
                user_ready = False

        purchased_products = Product.objects.none()
        if download_obj.free:
            can_download = True
            user_ready = True
        else:
            # not free
            purchased_products = ProductPurchase.objects.products_by_request(request)
            if download_obj.product in purchased_products:
                can_download = True
        if not can_download or not user_ready:
            messages.error(request, "You do not have access to download this item")
            return redirect(download_obj.get_default_url())

        aws_filepath = download_obj.generate_download_url()
        print(aws_filepath)
        return HttpResponseRedirect(aws_filepath)


class ProductDetailView(ObjectViewedMixin, DetailView):
    # queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        # context['abc'] = 123
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist")
        return instance


def product_detail_view(request, pk=None, *args, **kwargs):

    instance = Product.objects.get_by_id(pk)
    product_files = ProductFile.objects.all().filter(product=instance)

    if instance is None:
        raise Http404("Product doesn't exist")

    context = {
        'object': instance,
        "product_files": product_files
    }
    return render(request, "products/detail.html", context)
