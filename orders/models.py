# orders/models.py
from django.db import models
from accounts.models import Account
from store.models import Product
from coupons.models import Coupon


class Order(models.Model):
    PAYMENT_METHODS = (
        ("COD", "Cash on Delivery"),
        ("PAYU", "PayU"),
    )

    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    order_number = models.CharField(max_length=20, unique=True)

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS
    )

    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)

    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, null=True, blank=True
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="New"  # ✅ ONLY FIELD ADMIN CHANGES
    )

    is_ordered = models.BooleanField(default=False)
    ip = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)

    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    ordered = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name
