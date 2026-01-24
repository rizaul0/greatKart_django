from .models import Cart, CartItem
from .views import _cart_id

def cart_counter(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        count = CartItem.objects.filter(cart=cart, is_active=True).count()
    except Cart.DoesNotExist:
        count = 0

    return {'cart_items_count': count}
