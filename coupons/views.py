from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from cart.models import CartItem
from cart.views import _cart_id
from coupons.models import Coupon 

# Create your views here.
def apply_coupon(request):
    code = request.POST.get("coupon_code", "").upper()

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect("cart")

    if not coupon.is_valid():
        messages.error(request, "Coupon expired or usage limit reached.")
        return redirect("cart")

    cart_items = CartItem.objects.filter(
        cart__cart_id=_cart_id(request)
    )

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # 🔑 CHECK PRODUCT COMPATIBILITY
    applicable = False
    for item in cart_items:
        if coupon.products.filter(id=item.product.id).exists():
            applicable = True
            break

    if not applicable:
        messages.error(
            request,
            "This coupon does not apply to products in your cart."
        )
        return redirect("cart")

    # ✅ APPLY COUPON
    request.session["coupon_id"] = coupon.id
    messages.success(
        request,
        f"Coupon {coupon.code} applied ({coupon.discount_percent}% OFF)"
    )

    return redirect("cart")
    code = request.POST.get('coupon_code', '').upper()

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect('cart')

    if not coupon.is_valid():
        messages.error(request, "Coupon expired or usage limit reached.")
        return redirect('cart')
    
    cart_items = CartItem.objects.filter(
        cart__cart_id=_cart_id(request)
    )
    applicable = False
    for item in cart_items:
        if coupon.products.filter(id=item.product.id).exists():
            applicable = True
            break

    if not applicable:
        messages.error(
            request,
            "This coupon does not apply to products in your cart."
        )
        return redirect("cart")
    request.session['coupon_id'] = coupon.id
    messages.success(
        request,
        f"Coupon {coupon.code} applied ({coupon.discount_percent}% OFF)"
    )
    return redirect('cart')
