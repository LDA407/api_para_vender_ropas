from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product


UserAccount = get_user_model()


class WishList(models.Model):
    user = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name='profile')
    total_items = models.IntegerField(default=0)

    def __str__(self) -> str:
        return super().__str__()


class WishListItem(models.Model):
    user = models.ForeignKey(
            UserAccount, on_delete=models.CASCADE)
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()
