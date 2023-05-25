import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.product.models import Product
from apps.shopping_cart.models import Cart
from utils.countries import Countries


class AccountManegers(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
    
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        shop_cart = Cart.objects.create(user = user)
        shop_cart.save()

        return user
    
    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff=True
        user.is_superuser=True
        user.save()
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField('full_name', max_length=250)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AccountManegers()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'full_name']

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'accounts'
        # managed = True
        # verbose_name = 'ModelName'
        # verbose_name_plural = 'ModelNames'


# @receiver(post_save, sender=UserAccount)
# def set_user_type(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         UserProfile.objects.create(user=instance)


# class UserProfile(models.Model):
#     user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='profile')
#     full_name = models.CharField(max_length=255)
#     address_line_1 = models.CharField(max_length=250, default="")
#     address_line_1 = models.CharField(max_length=250, default="")
#     city = models.CharField(max_length=250, choices=Countries)
#     state_or_province = models.CharField(max_length=250, default="")
#     zip_code = models.CharField(max_length=20, default="")
#     telephone = models.CharField(max_length=30, blank=True, null=True)
#     additional_phone = models.CharField(max_length=30, blank=True, null=True)
#     profile_pic = models.ImageField(
#         # default='auth_user/user_picture_default.png',
#         upload_to=user_directory_path,
#         blank=True, null=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.user.get_full_name()

#     def get_full_name(self):
#         return self.full_name

#     def get_absolute_url(self):
#         return reverse('user_profile:profile', args=[self.slug])


class WishList(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)

    def __str__(self) -> str:
        return super().__str__()


class WishListItem(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()


class Review(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.comment