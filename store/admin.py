from django.contrib import admin
from .models import Product, Variant
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'is_available','modified_date')
    prepopulated_fields = {'slug': ('product_name',)}
    
admin.site.register(Product, ProductAdmin)

class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant_category', 'variant_value', 'is_active', 'created_date')
    list_editable = ('is_active',)
    list_filter = ('variant_category', 'is_active')
admin.site.register(Variant, VariantAdmin)

