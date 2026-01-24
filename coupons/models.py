from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)

    # OWNER CONTROLS THIS
    discount_percent = models.PositiveIntegerField(
        help_text="Enter discount percentage (e.g. 10 for 10%)"
    )

    # Optional cap
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )

    # Time control
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    # Usage control
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    # Product-specific coupons
    products = models.ManyToManyField(
        'store.Product',
        blank=True,
        help_text="Leave empty to apply on all products"
    )

    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.used_count < self.usage_limit
        )

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"


# Create your models here.
