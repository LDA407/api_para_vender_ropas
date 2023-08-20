import os
from datetime import datetime

from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.urls import reverse

class Tag(models.Model):
    class Meta:
        db_table = "tag"
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        db_table = "category"
        verbose_name_plural = 'Categories'
    parent = models.ForeignKey('self', related_name='children', on_delete = models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)

    def get_children(self):
        return Category.objects.filter(parent = self.id)

    def __str__(self):
        return self.name


class SharedFields(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    
    products = models.ManyToManyField('product.Product')

    def get_products(self):
        return self.products.all()

    def __str__(self):
        return self.name


class Tax(SharedFields):
    class Meta:
        db_table = "tax"
        verbose_name_plural = 'Taxes'

    tax_percentage = models.DecimalField(max_digits = 4, decimal_places = 2)


class Discount(SharedFields):
    class Meta:
        db_table = "discount"
        verbose_name_plural = 'Discounts'

    amount = models.DecimalField(max_digits = 4, decimal_places = 2)


class GaleryProduct(models.Model):
    class Meta:
        db_table = "galery_product"
        verbose_name_plural = 'Galery Products'

    product = models.ForeignKey('product.Product', blank=True, null=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to = "media")
    thumbnail = models.BooleanField(default = False)


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

    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    available_colors = models.ManyToManyField(ColorVariation, blank=True)
    available_sizes = models.ManyToManyField(SizeVariation, blank=True)
    date_created = models.DateTimeField(default=datetime.now)

    def get_discount(self):
        discount_set = Discount.objects.filter(is_active = True)
        discounts = sum([i.amount for i in discount_set if self in i.get_products()])
        return discounts

    def get_taxes(self):
        taxes_set = Tax.objects.filter(is_active = True)
        taxes = [i for i in taxes_set if self in i.get_products()]
        return taxes

    def mark_as_sold(self, value):
        self.sold += value
        self.save()

    def get_gallery(self):
        gallery = GaleryProduct.objects.filter(product_id = self.id)
        return gallery

    def get_colors(self):
        available_colors = self.available_colors.all()
        if available_colors:
            return available_colors
        return ''

    def get_sizes(self):
        available_sizes = self.available_sizes.all()
        if available_sizes:
            return available_sizes
        return ''

    # def get_absolute_url(self):
    #     return reverse('detail', kwargs={
    #         'slug': self.slug
    #     })

    def __str__(self) -> str:
        return self.name

