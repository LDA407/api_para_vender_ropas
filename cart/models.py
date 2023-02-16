from django.db import models
from django.conf import settings
from product.models import Product

User = settings.AUTH_USER_MODEL
# Create your models here.

class Cart(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE )
	total_items = models.IntegerField(default=0)


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	count = models.IntegerField()

	def product_not_available(self):
		return (self.count > self.product.quantity)

	def raw_total_price(self):
		return (float(self.product.price) * float(self.count))
	
	def raw_total_compare_price(self):
		return (float(self.product.price_with_discount) * float(self.count))

	def get_total_item_price(self):
		price =  self.raw_total_price()
		price_with_discount =  self.raw_total_compare_price()

		return {
			'price': f'{price:.2f}',
			'price_with_discount': f'{price_with_discount:.2f}'
		}