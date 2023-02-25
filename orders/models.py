import uuid
from django.db import models
from shipping.models import Shipping
from product.models import Product
from datetime import datetime
from django.contrib.auth import get_user_model
from utils.countries import Countries 

User = get_user_model()


class Order(models.Model):
	class OrderStatus(models.TextChoices):
		NOT_PROCESSED = 'not_processed'
		PROCESSED = 'processed'
		SHIPPING = 'shipping'
		DELIVEDER = 'delivered'
		CANCELLED = 'cancelled'
	# id = models.UUIDField(default=uuid.uuid4, primary_key=True)
	status = models.CharField(
		max_length = 50,
		choices = OrderStatus.choices,
		default = OrderStatus.NOT_PROCESSED
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	transaction_id = models.CharField(max_length = 255, unique=True)
	amount = models.DecimalField(max_digits = 5, decimal_places = 2)
	full_name = models.CharField(max_length = 255)
	address_line_1 = models.CharField(max_length = 255)
	address_line_2 = models.CharField(max_length = 255, blank=True)
	city = models.CharField(max_length = 255)
	province = models.CharField(max_length = 255)
	zip_code = models.CharField(max_length = 255)
	country = models.CharField(
		max_length = 255,
		choices = Countries.choices,
		default = Countries.Canada
	)
	telephone = models.CharField(max_length = 255)
	shipping_name = models.CharField(max_length = 255)
	shipping_time = models.CharField(max_length = 255)
	shipping_price = models.DecimalField(max_digits = 5, decimal_places = 2)
	date_issued = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.reference_number
	
	@property
	def reference_number(self):
		return f'ORDER - {self.pk}'


class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	name = models.CharField(max_length = 255)
	price = models.DecimalField(max_digits = 5, decimal_places = 2)
	count = models.IntegerField()
	data_added = models.DateTimeField(auto_now_add=True)

