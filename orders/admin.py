# orders/admin.py
from django.contrib import admin
from .models import Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = (
        "product",
        "color",
        "size",
        "quantity",
        "product_price",
        "user",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "coupon",
        "payment_method",
        "order_total",
        "discount",
        "tax",
        "status",
        "is_ordered",
        "created_at",
    )

    readonly_fields = (
        "user",
        "coupon",
        "order_number",
        "payment_method",
        "order_total",
        "discount",
        "tax",
        "ip",
        "created_at",
        "is_ordered",
    )

    list_filter = ("status", "payment_method", "created_at")


    inlines = [OrderProductInline]
