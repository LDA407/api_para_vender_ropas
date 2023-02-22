import os
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from cart.models import Cart

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
