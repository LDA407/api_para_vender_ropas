from django.contrib import admin
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'is_staff', 'is_superuser', 'is_active')
    list_display_links = ('full_name', 'email')
    search_fields = ('full_name', 'email', 'is_staff', 'is_superuser', 'is_active')
    # list_filter = 
    list_per_page = 25

admin.site.register(User, UserAdmin)