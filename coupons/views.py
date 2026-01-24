from pyexpat.errors import messages
from django.shortcuts import render
from django.shortcuts import redirect
from coupons.models import Coupon

# Create your views here.
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').upper()

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect('cart')

    if not coupon.is_valid():
        messages.error(request, "Coupon expired or usage limit reached.")
        return redirect('cart')

    request.session['coupon_id'] = coupon.id
    messages.success(
        request,
        f"Coupon {coupon.code} applied ({coupon.discount_percent}% OFF)"
    )
    return redirect('cart')
