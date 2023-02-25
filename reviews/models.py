from datetime import datetime
from django.db import models
from product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Review(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating     = models.DecimalField(max_digits=2, decimal_places=1)
    comment    = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return self.comment



