from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.urls import reverse
from products.models import Product
from reviews.forms import ReviewForm
from reviews.models import Review


@login_required()
def create_review_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review_obj = Review.objects.get(user=request.user, product=product)
                if form.cleaned_data["image"]:
                    review_obj.image = form.cleaned_data["image"]
                if form.cleaned_data["review"]:
                    review_obj.review = form.cleaned_data["review"]
                if form.cleaned_data["rating"]:
                    review_obj.rating = form.cleaned_data["rating"]
                review_obj.save()
            except Review.DoesNotExist:
                Review.objects.create(review=form.cleaned_data["review"],
                                      rating=form.cleaned_data["rating"],
                                      image=form.cleaned_data["image"],
                                      product=product,
                                      user=request.user,
                                      )
            return HttpResponseRedirect(reverse("reviews:thanks"))
    else:
        form = ReviewForm()

    context = {
        "form": form,
        "product": product,
    }

    return render(request, "reviews/create_review.html", context)


def thanks(request):
    return render(request, "reviews/thanks.html", {})
