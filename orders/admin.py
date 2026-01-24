from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'amount', 'payment_method', 'status', 'created_at')
    search_fields = ('order_id', 'user__username')
    list_filter = ('status', 'created_at')
admin.site.register(Payment, PaymentAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'order_total', 'tax', 'status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'user__username')
    list_filter = ('status', 'is_ordered', 'created_at')
admin.site.register(Order, OrderAdmin)

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'user', 'quantity', 'product_price', 'ordered')
    search_fields = ('product__product_name', 'order__order_number', 'user__username')
    list_filter = ('ordered',)

admin.site.register(OrderProduct, OrderProductAdmin)