from django.shortcuts import get_object_or_404, render
from cart.models import CartItem
from category.models import Category
from orders.models import Order
from store.models import Product
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from cart.views import _cart_id

def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

# customer search views
def search_results(request):
    keyword = request.GET.get("keyword", "")
    products = Product.objects.filter(is_available=True)

    # ✅ KEYWORD SEARCH
    if keyword:
        products = products.filter(product_name__icontains=keyword)

    # ✅ PRICE FILTER
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # ✅ PAGINATION
    paginator = Paginator(products, 5)
    page_number = request.GET.get("page")
    page_products = paginator.get_page(page_number)

    return render(request, "search-result.html", {
        "products": page_products,
        "product_count": products.count(),
    })



def store(request, category_slug=None):
    category = None
    products = Product.objects.filter(is_available=True)

    # ✅ CATEGORY FILTER
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # ✅ PRICE FILTER
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # ✅ PAGINATION
    paginator = Paginator(products, 5)
    page_number = request.GET.get("page")
    page_products = paginator.get_page(page_number)

    context = {
        "products": page_products,
        "product_count": products.count(),
    }

    return render(request, "store.html", context)
# customer product detail views
def product_detail(request , category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug )
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Product.DoesNotExist:
        single_product = None
    return render(request, 'product-detail.html', {'product': single_product, 'in_cart': in_cart})



@login_required(login_url='signin')
def dashboard(request ):
    orders =  Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    return render(request, 'dashboard.html', {'orders': orders})