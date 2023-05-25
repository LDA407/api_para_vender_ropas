import os
from datetime import datetime

from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.urls import reverse


class ProductManager(models.Manager):

    def search_query(self, search_query):
        return self.filter(
            models.Q(description__icontains=search_query) |
            models.Q(name__icontains=search_query)
        )


# from django.core.validators import RegexValidator

# def validate_letters(value):
#     if not value.isalpha():
#         raise ValidationError("El campo debe contener solo letras.")


class Tag(models.Model):
    class Meta:
        db_table = "tag"
    name = models.CharField(max_length=250,unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        db_table = "category"
        verbose_name_plural = 'Categories'
    parent = models.ForeignKey('self', related_name='children', on_delete = models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)

    @classmethod
    def get_sub_categories(cls, instance):
        return list(cls.objects.filter(parent=instance))

    def __str__(self):
        return self.name


class Tax(models.Model):
    class Meta:
        db_table = "tax"
        verbose_name_plural = 'Taxes'
    name = models.CharField(max_length=100, blank=False, null=False)
    tax_porcentage = models.DecimalField(max_digits = 4, decimal_places = 2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Discount(models.Model):
    class Meta:
        db_table = "discount"
        verbose_name_plural = 'Discounts'
    name = models.CharField(max_length=100, blank=False, null=False)
    amount = models.DecimalField(max_digits = 4, decimal_places = 2)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class GaleryProduct(models.Model):
    class Meta:
        db_table = "galery_product"
        verbose_name_plural = 'Galery Products'
    image = models.ImageField(upload_to="media")


class ColorVariation(models.Model):
    class Meta:
        db_table = "color_variation"
        verbose_name_plural = 'Colors Variations'
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SizeVariation(models.Model):
    class Meta:
        db_table = "size_variation"
        verbose_name_plural = 'Sizes Variations'
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        db_table = "product"

    name = models.CharField(max_length=250)
    description = RichTextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.ForeignKey(Discount, blank=True, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    galery = models.ForeignKey(GaleryProduct, blank=True, null=True, on_delete=models.CASCADE)
    available_colors = models.ManyToManyField(ColorVariation, blank=True, null=True)
    available_sizes = models.ManyToManyField(SizeVariation, blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)

    objects = models.Manager()
    products = ProductManager()

    # def get_discounted_price(self):
    #     discounts = self.discount_set.all()
    #     if discounts:
    #         discount = max(discounts, key=lambda discount: discount.amount)
    #         return self.price - discount.amount
    #     return self.price

    # def calculate_price_with_taxes(self):
    #     taxes = self.tax_set.all()
    #     if taxes:
    #         tax = max(taxes, key=lambda tax: tax.tax_porcentage)
    #         return self.price * tax.tax_porcentage
    #     return self.price

    def mark_as_sold(self):
        self.sold += 1
        self.save()

    # def get_image(self, request):
    #     if self.photo:
    #         return str(request.build_absolute_uri(self.photo.url))
    #     return ""

    # def get_absolute_url(self):
    #     return reverse('detail', kwargs={
    #         'slug': self.slug
    #     })

    def get_like_url(self):
        return reverse('like', kwargs={
            'slug': self.slug
        })

    @property
    def comments(self):
        return self.comment_set.all()

    @property
    def comments_count(self):
        return self.comment_set.all().count()

    @property
    def likes_count(self):
        return self.like_set.all().count()

    def __str__(self) -> str:
        return self.name

