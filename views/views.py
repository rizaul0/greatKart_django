from django.shortcuts import get_object_or_404, render
from category.models import Category
from store.models import Product
# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def register(request):
    return render(request, 'register.html')
def signin(request):
    return render(request, 'signin.html')
def dashboard(request):
    return render(request, 'dashboard.html')
def order_complete(request):
    return render(request, 'order_complete.html')
def place_order(request):
    return render(request, 'place-order.html')
def search_results(request):
    return render(request, 'search-result.html')
def store(request, category_slug=None):
    category = None
    products = None 
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all()
        product_count = products.count()
    return render(request, 'store.html', {'products': products, 'product_count': product_count})
def product_detail(request , category_slug, product_slug):
    product = get_object_or_404(Product,category__slug=category_slug, slug=product_slug , )
    return render(request, 'product-detail.html', {'product': product })