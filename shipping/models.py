from django.db import models

# Create your models here.
class Shipping(models.Model):
	class Meta:
		verbose_name = 'Shipping'
		verbose_name_plural = 'Shipping'
	
	name = models.CharField(max_length=225, unique=True)
	time_to_delivery = models.CharField(max_length=225)
	price = models.DecimalField(max_digits=5, decimal_places=2)

