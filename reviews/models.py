from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth import get_user_model

from products.models import Product

Rating_CHOICES = (
    (1, 'Poor'),
    (2, 'Average'),
    (3, 'Good'),
    (4, 'Very Good'),
    (5, 'Excellent')
)

User = get_user_model()


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=Rating_CHOICES, default=1)
    review = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to="review/")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title
