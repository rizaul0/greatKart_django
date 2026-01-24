from django.db import models
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.email if self.user else self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    variation = models.ManyToManyField('store.Variant', blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE ,null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.product_name
    
 
   