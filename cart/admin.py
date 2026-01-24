from django.contrib import admin

from cart.models import Cart, CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_added')
admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')
    list_editable = ('quantity', 'is_active')
    list_filter = ('is_active',)
admin.site.register(CartItem, CartItemAdmin)