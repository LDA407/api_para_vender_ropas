from django.contrib import admin
from .models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'parent')
    list_display_links = ('id','name', 'parent')
    search_fields = ('name', 'parent')
    list_per_page = 25


class ProductAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'name', 'price_with_discount', 'quantity', 'sold', 'price', )
    list_display_links = ( 'id', 'name', )
    list_filter = ( 'category', )
    list_editable = ( 'price_with_discount', 'price', 'quantity', )
    search_fields = ('name', 'description')
    list_per_page = 20


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
