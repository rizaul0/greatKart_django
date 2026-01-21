from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    brand_name = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variant_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variant_category='size', is_active=True)
    
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_category = models.CharField(max_length=100, choices=[('color', 'Color'), ('size', 'Size')])
    variant_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    objects = VariationManager()

    def __str__(self):
        return f"{self.variant_category}: {self.variant_value}"
