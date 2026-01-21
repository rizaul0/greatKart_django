
from category.models import Category
from cart.models import Cart, CartItem
def get_categories(request):
    
    categories = Category.objects.all()
    return {'categories': categories}
def get_brands(request):
    
    brands = Category.objects.values_list('name', flat=True).distinct()
    return {'brands': brands}

def cart_count(request):
    
    cart_items_count = 0
    try:
        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items_count = CartItem.objects.filter(cart=cart).count()
    except Cart.DoesNotExist:
        cart_items_count = 0
    return {'cart_items_count': cart_items_count}