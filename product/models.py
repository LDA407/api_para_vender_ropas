import os
from django.db import models
from django.conf import settings
from datetime import datetime

# Create your models here.
# def _directory_path(instance, filename):
#     _picture_name = f'{instance.name}_thumbnails.jpg'
#     full_path = os.path.join(settings.STATIC_ROOT, _picture_name)
#     if os.path.exists(full_path):
#         os.remove(full_path)
#     return _picture_name


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250)
    photo = models.ImageField(upload_to='media')
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    price_with_discount = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    quantity = models.IntegerField(default= 0)
    sold = models.IntegerField(default= 0)
    date_created = models.DateTimeField(default=datetime.now)

    def get_image(self):
        if self.photo:
            return 'http://127.0.0.1:8000/static' + self.photo.url
        return ""
    
    def __str__(self) -> str:
        return self.name

