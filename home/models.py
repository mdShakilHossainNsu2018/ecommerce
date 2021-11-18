from django.db import models

from products.models import Product


class CarouselProduct(models.Model):
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="carousel/")
    url = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


