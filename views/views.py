from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account
from cart.models import Cart, CartItem
from category.models import Category
from store.models import Product
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        city = request.POST['city']
        country = request.POST['country']
        gender = request.POST.get('gender', 'M')

        # validations
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        if Account.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        # create user
        user = Account.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )

        user.city = city
        user.country = country
        user.gender = gender
        user.is_active = True   # customer account
        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('signin')

    return render(request, 'register.html')
def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('signin')

    return render(request, 'signin.html')
def logout_user(request):
    logout(request)
    return redirect('home')
@login_required(login_url='signin')
def dashboard(request):
    return render(request, 'dashboard.html')
def order_complete(request):
    return render(request, 'order_complete.html')
def place_order(request):
    cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))
    total_price = sum(item.sub_total() for item in cart_items)
    tax = (total_price * Decimal(0.09)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax': tax,
        'grand_total': total_price + tax,
    }
    return render(request, 'place-order.html', context)
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

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart')



def  cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (total * Decimal(0.09)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = total + tax

    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0

    context = {
        
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'cart.html', context)

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    # If cart still has items → stay on cart page
    if CartItem.objects.filter(cart=cart).exists():
        return redirect('cart')
    else:
        return redirect('store')





# owner app views
@login_required
def owner_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    products = Product.objects.all()
    Categorys = Category.objects.all()
    return render(request, 'owneradmin/dashboard.html', {'products': products, 'Categorys': Categorys})
@login_required
def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            product_name=request.POST['product_name'],
            slug=request.POST['slug'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            category_id=request.POST['category'],
            image=request.FILES['image'],
            description=request.POST['description'],
        )
        return redirect('owner_dashboard')

    categories = Category.objects.all()
    return render(request, 'owneradmin/add_product.html', {'categories': categories})
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.product_name = request.POST['product_name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.category_id = request.POST['category']
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        return redirect('owner_dashboard')

    categories = Category.objects.all()
    return render(request, 'owneradmin/edit_product.html', {
        'product': product,
        'categories': categories
    })
@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('owner_dashboard')





@login_required(login_url='signin')
def add_category(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        cat_image = request.FILES.get('cat_image')

        slug = slugify(name)

        Category.objects.create(
            name=name,
            slug=slug,
            description=description,
            cat_image=cat_image
        )
        return redirect('store')

    return render(request, 'owneradmin/add_category.html')
@login_required(login_url='signin')
def edit_category(request, category_id):
    if not request.user.is_staff:
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST['name']
        category.slug = slugify(category.name)
        category.description = request.POST.get('description', '')

        if 'cat_image' in request.FILES:
            category.cat_image = request.FILES['cat_image']

        category.save()
        return redirect('store')

    return render(request, 'owneradmin/edit_category.html', {'category': category})
@login_required(login_url='signin')
def delete_category(request, category_id):
    if not request.user.is_staff:
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('store')

    return render(request, 'owneradmin/delete_category.html', {'category': category})

