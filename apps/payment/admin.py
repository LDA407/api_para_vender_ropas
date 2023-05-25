from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
	def has_delete_permission(self, request , obj = None):
		return False
	
	list_display = ('id', 'transaction_id', 'amount', 'status')
	list_display_links = ('id', 'transaction_id', )
	list_filter = ('status', )
	list_editable = ('status', )
	list_per_page = 25

admin.site.register(Order, OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
	def has_delete_permission(self, request , obj = None):
		return False
	
	list_display = ('id', 'name', 'price', 'count')
	list_display_links = ('id', 'name', )
	list_per_page = 25

admin.site.register(OrderItem ,OrderItemAdmin)


from django.contrib import admin
from .models import FixedPriceCoupon, PorcentageCoupon


class FixedPriceCouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount_amount')
    list_display_links = ('name',)
    list_editable = ('discount_amount',)
    search_fields = ('name',)
    list_per_page: 25


class PorcentageCouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount_porcentage')
    list_display_links = ('name',)
    list_editable = ('discount_porcentage',)
    search_fields = ('name',)
    list_per_page: 25


admin.site.register(FixedPriceCoupon, FixedPriceCouponAdmin)

admin.site.register(PorcentageCoupon, PorcentageCouponAdmin)
