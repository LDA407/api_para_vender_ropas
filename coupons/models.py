from django.db import models

# Create your models here.
class FixedPriceCoupon(models.Model):
    name = models.CharField(max_length=255, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return super().__str__()


class PorcentageCoupon(models.Model):
    name = models.CharField(max_length=255, unique=True)
    discount_porcentage = models.IntegerField()

    def __str__(self) -> str:
        return super().__str__()