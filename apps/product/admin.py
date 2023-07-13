from django.contrib import admin
from .models import *
# from import_export import resources
# from import_export.admin import ImportExportModelAdmin


# class CategoryResource(resources.ModelResource):  
#    class Meta:  
#      model = Category


# class ProductResource(resources.ModelResource):  
#    class Meta:  
#      model = Product


class SubcategoryInline(admin.TabularInline):
    model = Category
    fields = ('name', 'parent')
    readonly_fields = fields
    extra = 0
    # show_change_link = True


class CategoryAdmin(
    # ImportExportModelAdmin,
    admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name', 'parent')
    list_per_page = 25
    inlines = [SubcategoryInline]
    # resource_clase = CategoryResource


class GaleryInline(admin.TabularInline):
    model = GaleryProduct
    extra = 4

class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_percentage')
    filter_horizontal = ('products',)


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount')
    filter_horizontal = ('products',)


class ProductAdmin(
    # ImportExportModelAdmin,
    admin.ModelAdmin):
    list_display = ( 'id', 'name', 'quantity', 'sold', 'price', )
    list_display_links = ( 'id', 'name', )
    list_filter = ( 'category', )
    list_editable = ('price', 'quantity', )
    search_fields = ('name', 'description')
    list_per_page = 20
    inlines = [GaleryInline]
    filter_horizontal = ('available_colors', 'available_sizes')
    # resource_clase = ProductResource


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.register(Tax, TaxAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(GaleryProduct)
admin.site.register(ColorVariation)
admin.site.register(SizeVariation)
admin.site.register(Product, ProductAdmin)
