# Register your models here.
from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_percent',
        'usage_limit', 'used_count',
        'valid_from', 'valid_to',
        'is_active'
    )
    list_filter = ('is_active',)
    search_fields = ('code',)
    filter_horizontal = ('products',)
