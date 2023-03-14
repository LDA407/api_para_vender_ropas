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


class CategoryAdmin(
    # ImportExportModelAdmin,
    admin.ModelAdmin):
    list_display = ('id','name', 'parent')
    list_display_links = ('id','name', 'parent')
    search_fields = ('name', 'parent')
    list_per_page = 25
    # resource_clase = CategoryResource


class ProductAdmin(
    # ImportExportModelAdmin,
    admin.ModelAdmin):
    list_display = ( 'id', 'name', 'quantity', 'sold', 'price', )
    list_display_links = ( 'id', 'name', )
    list_filter = ( 'category', )
    list_editable = ('price', 'quantity', )
    search_fields = ('name', 'description')
    list_per_page = 20
    # resource_clase = ProductResource


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.register(Tax)
admin.site.register(Discount)
admin.site.register(GaleryProduct)
admin.site.register(ColorVariation)
admin.site.register(SizeVariation)
admin.site.register(Product, ProductAdmin)
