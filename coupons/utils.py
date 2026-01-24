from decimal import Decimal


def calculate_coupon_discount(cart_items, coupon):
    discount_total = Decimal('0.00')

    for item in cart_items:
        # Product-specific check
        if coupon.products.exists() and item.product not in coupon.products.all():
            continue

        item_total = item.sub_total()
        discount = (item_total * coupon.discount_percent) / 100

        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)

        discount_total += discount

    return discount_total
