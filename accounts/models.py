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


# https://docs.djangoproject.com/en/4.0/ref/models/fields/
"""
class UserProfile(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    DNI_TYPE = Choices(
        ('dni', _('national identification document')),
        ('civic book', _('Civic Book')),
        ('book enlistment', _('Book enlistment')),
        ('passport', _('Passport')))
    GENDER = Choices(
        ('man', _('Man')),
        ('woman', _('Woman')),
        ('other', _('Other')))
    MSTATUS = Choices(
        ('married', _('Married')),
        ('separated/divorced', _('Separated/Divorced')),
        ('single', _('Single')),
        ('free union', _('Free Union')),
        ('widower', _('Widower')))
    user = models.OneToOneField('auth_user.UserAccount', on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(_("full name"), max_length=255)
    identity_card = models.CharField(_("identity card"), max_length=50, choices=DNI_TYPE, default=DNI_TYPE.dni)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    gender = models.CharField(_("gender"), max_length=50, choices=GENDER, default=GENDER.man)
    marital_status = models.CharField(_("marital status"), max_length=50, choices=MSTATUS, blank=True, null=True)
    telephone = models.CharField(_("telephone"), max_length=30, blank=True, null=True)
    additional_phone = models.CharField(_("additional phone"), max_length=30, blank=True, null=True)
    profile_pic = models.ImageField(
        _('profile picture'),
        default='auth_user/user_picture_default.png',
        upload_to=user_directory_path,
        blank=True, null=True
    )
    nacionality = models.CharField(_("nacionality"), max_length=100, blank=True, null=True)
    province = models.ForeignKey('contact.Province', blank=True, null=True, on_delete=models.PROTECT)
    department = models.ForeignKey('contact.Department', blank=True, null=True, on_delete=models.PROTECT)
    address = models.CharField(_("address"), max_length=250, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    # slug = AutoSlugField(populate_from='id', unique_with=['user__id', 'user__email'],)

    def __str__(self):
        return self.user.get_full_name()

    def get_full_name(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('auth_user:profile', args=[self.slug])

"""
