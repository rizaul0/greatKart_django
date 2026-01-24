from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from decimal import Decimal, ROUND_HALF_UP
from coupons.models import Coupon
from coupons.utils import calculate_coupon_discount
from store.models import Product, Variant
# Create your views here.

# private function to get cart id
def _cart_id(request):
    # Logged-in user → persistent cart
    if request.user.is_authenticated:
        return f"user_{request.user.id}"

    # Guest user → session cart
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# customer cart views

def cart(request, total=0, quantity=0, cart_items=None):
    coupon = None
    discount = Decimal('0.00')

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity

        # APPLY COUPON
        if 'coupon_id' in request.session:
            coupon = Coupon.objects.filter(
                id=request.session['coupon_id']
            ).first()

            if coupon and coupon.is_valid():
                discount = calculate_coupon_discount(cart_items, coupon)
            else:
                request.session.pop('coupon_id', None)

        tax = ((total - discount) * Decimal('0.09')).quantize(Decimal('0.01'))
        grand_total = total - discount + tax

    except Cart.DoesNotExist:
        cart_items = []
        total = quantity = tax = grand_total = discount = 0
        
    # 🚨 Remove coupon if cart is empty
    if not cart_items and 'coupon_id' in request.session:
       del request.session['coupon_id']


    context = {
        'cart_items': cart_items, 
        'total': total,
        'quantity': quantity,
        'discount': discount,
        'tax': tax,
        'grand_total': grand_total,
        'coupon': coupon,
    }

    return render(request, 'cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variations = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variant.objects.get(
                    product=product,
                    variant_category__iexact=key,
                    variant_value__iexact=value
                )
                product_variations.append(variation)
            except Variant.DoesNotExist:
                pass

    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        existing_variations = list(item.variation.all())
        if existing_variations == product_variations:
            # SAME VARIANT → increase quantity
            item.quantity += 1
            item.save()
            return redirect('cart')

    # DIFFERENT VARIANT → create new cart item
    cart_item = CartItem.objects.create(
        product=product,
        quantity=1,
        cart=cart
    )
    if product_variations:
        cart_item.variation.set(product_variations)

    cart_item.save()
    return redirect('cart')



def increment_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.quantity += 1
    cart_item.save()

    return redirect('cart')

# customer remove cart views

def remove_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')




# customer remove cart views

def remove_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.delete()

    # If cart still has items → stay on cart page
    if not CartItem.objects.filter(cart=cart).exists():
        request.session.pop('coupon_id', None)
        return redirect('store')

    return redirect('cart')


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



def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    return redirect('cart')
