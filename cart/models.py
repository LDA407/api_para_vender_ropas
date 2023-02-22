from django.db import models
from decimal import Decimal
from django.conf import settings
from product.models import Product
from django.db.models import Count, F, Value, DecimalField
User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_amount(self):
        return self.cartitem_set.aggregate(
            total=models.Sum(F('product__price') * F('count'), output_field=DecimalField())
        )['total'] or Decimal(0)

    def get_total_compare_amount(self):
        return self.cartitem_set.aggregate(
            total=models.Sum(F('product__get_discounted_price') * F('count'), output_field=DecimalField())
        )['total'] or Decimal(0)

    def __str__(self):
        return f"Cart for user {self.user.full_name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()

    def product_not_available(self):
        if self.count > self.select_related("product").values("quantity"):
            return self.select_related("product").values("name")

    def raw_total_amount(self):
        return float(self.select_related("product").values("price")) * float(self.count)


    def __str__(self):
        return f"{self.count}x {self.product.name} in cart for {self.cart.user.full_name}"
