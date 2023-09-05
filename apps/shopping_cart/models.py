from django.shortcuts import get_object_or_404
from django.db import models
from decimal import Decimal
from django.conf import settings
from apps.product.models import Product
from django.db.models import Count, F, Value, DecimalField
User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    class Meta:
        db_table = 'shopping_cart'
        verbose_name = 'Shopping Cart'
        # permissions = [('can_deliver_pizzas', 'Can deliver pizzas')]
        # indexes = [
        #     models.Index(fields=['last_name', 'first_name']),
        #     models.Index(fields=['first_name'], name='first_name_idx'),
        # ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_cart_items(self):
        return self.cartitem_set.all()
    
    def add_cart_item(self, product, count):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_item.count += count
            cart_item.save()

    def delete_cart_item(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear_cart_items(self):
        self.cartitem_set.all().delete()
    
    def get_total_items(self):
        return self.cartitem_set.all().count()

    def _item_exists(self, product):
        return self.cartitem_set.filter(product = product).exists()

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
    class Meta:
        db_table = 'cartitem'
        # verbose_name = 'Shopping Cart'

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()

    def product_not_available(self):
        if self.count > self.product.quantity:
            return self.product.name

    def __str__(self):
        return f"{self.count}x {self.product.name} in cart for {self.cart.user.full_name}"
