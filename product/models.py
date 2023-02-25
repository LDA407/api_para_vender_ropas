import os
from django.db import models
from django.conf import settings
from datetime import datetime
from django.urls import reverse

# Create your models here.
# def _directory_path(instance, filename):
#     _picture_name = f'{instance.name}_thumbnails.jpg'
#     full_path = os.path.join(settings.STATIC_ROOT, _picture_name)
#     if os.path.exists(full_path):
#         os.remove(full_path)
#     return _picture_name


class ProductManager(models.Manager):
    def _the_product_exists(self, product_id):
        return self.filter(product_id=product_id).exists()

    def search_query(self, search_query):
        return self.filter(
            models.Q(description__icontains=search_query) |
            models.Q(name__icontains=search_query)
        )



class Tag(models.Model):
    class Meta:
        db_table = "tag"
    name = models.CharField(max_length=250, blank=False, null=False, unique=True)


class Category(models.Model):
    class Meta:
        db_table = "category"
        verbose_name_plural = 'Categories'
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Tax(models.Model):
    class Meta:
        db_table = "tax"
        verbose_name_plural = 'Taxes'
    name = models.CharField(max_length=100, blank=False, null=False)
    tax_porcentage = models.DecimalField(max_digits = 4, decimal_places = 2) 


class Discount(models.Model):
    class Meta:
        db_table = "discount"
        verbose_name_plural = 'Discounts'
    name = models.CharField(max_length=100, blank=False, null=False)
    amount = models.DecimalField(max_digits = 4, decimal_places = 2) 


class GaleryProduct(models.Model):
    class Meta:
        db_table = "galery_product"
        verbose_name_plural = 'GaleriesProducts'
    image = models.ImageField(upload_to="media")


class ColorVariation(models.Model):
    class Meta:
        db_table = "color_variation"
        verbose_name_plural = 'ColorsVariations'
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SizeVariation(models.Model):
    class Meta:
        db_table = "size_variation"
        verbose_name_plural = 'SizesVariations'
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        db_table = "product"
    name = models.CharField(max_length=250)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.ForeignKey(Discount, blank=True, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    galery = models.ManyToManyField(GaleryProduct, blank=True, null=True)
    available_colours = models.ManyToManyField(ColorVariation, blank=True, null=True)
    available_sizes = models.ManyToManyField(SizeVariation, blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)

    objects = models.Manager()
    products = ProductManager()

    def get_discounted_price(self):
        discounts = self.discount_set.all()
        if discounts:
            discount = max(discounts, key=lambda d: d.amount)
            return self.price - discount.amount
        return self.price

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


class Comment(models.Model):
    # class Meta:
        # db_table = "comment"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.user.username


class Like(models.Model ):
    # class Meta:
        # db_table = "like"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username