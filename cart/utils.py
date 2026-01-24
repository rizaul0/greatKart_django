# cart/utils.py

def cart_id(request):
    if request.user.is_authenticated:
        return f"user_{request.user.id}"

    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
