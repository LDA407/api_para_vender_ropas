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
