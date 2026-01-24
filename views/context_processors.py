
from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id
def get_categories(request):
    
    categories = Category.objects.all()
    return {'categories': categories}
def get_brands(request):
    
    brands = Category.objects.values_list('name', flat=True).distinct()
    return {'brands': brands}

def cart_count(request):
    count = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        count = CartItem.objects.filter(cart=cart, is_active=True).count()
    except Cart.DoesNotExist:
        pass
    return {'cart_items_count': count}
