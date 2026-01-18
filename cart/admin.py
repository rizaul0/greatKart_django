from django.contrib import admin

from cart.models import Cart

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
admin.site.register(Cart, CartAdmin)