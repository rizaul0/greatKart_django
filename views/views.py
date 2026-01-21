from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Account, PasswordResetToken
from cart.models import Cart, CartItem
from category.models import Category
from store.models import Product, Variant
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.timezone import now
from accounts.models import Account
# Create your views here.





# customer app views
def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})



# customer auth views
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



# customer auth views

def signin(request):
    # STEP 1 — PASSWORD SUBMISSION
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, 'Invalid email or password')
            return redirect('signin')

        # Generate 6-digit OTP
        otp = random.randint(100000, 999999)

        # Store OTP + user in session
        request.session['login_otp'] = str(otp)
        request.session['otp_user_id'] = user.id

        # Send OTP email
        send_mail(
            subject="Your OTP for GreatKart Login",
            message=f"""
Hello {user.first_name},

Your One-Time Password (OTP) is:

🔐 {otp}

This OTP is valid for one login attempt.

If you did not try to log in, please ignore this email.

Regards,
GreatKart Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email")
        return render(request, 'verify_otp.html')  # OTP input page

    # STEP 2 — OTP VERIFICATION
    if request.method == 'POST' and 'otp' in request.POST:
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('login_otp')
        user_id = request.session.get('otp_user_id')

        if not session_otp or not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('signin')

        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP")
            return render(request, 'verify_otp.html')

        # OTP VALID → LOGIN USER
        user = Account.objects.get(id=user_id)
        login(request, user)

        # Update last_login
        user.last_login = now()
        user.save()
        login_time = timezone.localtime(timezone.now())
        # Send successful login email
        send_mail(
            subject="Successful Login – GreatKart",
            message=f"""
Hello {user.first_name},

You have successfully logged in to your GreatKart account.

📅 Date & Time: {login_time.strftime('%d %b %Y, %I:%M %p')} (IST)
📧 Email: {user.email}

If this was not you, please reset your password immediately.

Regards,
GreatKart Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Clean session
        request.session.pop('login_otp', None)
        request.session.pop('login_email', None)


        messages.success(request, "Login successful")
        return redirect('home')

    # STEP 0 — NORMAL GET REQUEST
    return render(request, 'signin.html')

# custom forgot password views

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, "Email not found")
            return redirect('forgot_password')

        token = PasswordResetToken.objects.create(user=user)

        reset_link = f"http://127.0.0.1:8000/reset-password/{token.token}/"

        send_mail(
            subject="Reset your GreatKart password",
            message=f"Click the link to reset your password:\n\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, "Password reset link sent to your email")
        return redirect('signin')

    return render(request, 'auth/forgot_password.html')


# custom password reset views
def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
    except PasswordResetToken.DoesNotExist:
        return HttpResponse("Invalid or expired link")

    if reset_token.is_expired():
        return HttpResponse("Reset link expired")

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect(request.path)

        user = reset_token.user
        user.set_password(password)
        user.save()

        reset_token.is_used = True
        reset_token.save()

        messages.success(request, "Password reset successful")
        return redirect('signin')

    return render(request, 'auth/reset_password.html')





# customer auth views
def logout_user(request):
    logout(request)
    return redirect('home')


# customer dashboard views
@login_required(login_url='signin')
def dashboard(request):
    return render(request, 'dashboard.html')


# customer order_complete views
@login_required(login_url='signin')
def order_complete(request):
    return render(request, 'order_complete.html')



# customer place order views
@login_required(login_url='signin')
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


# customer search views
def search_results(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')
        if keyword:
            products = Product.objects.filter(product_name__icontains=keyword)
            product_count = products.count()
            paginator = Paginator(products, 5)  # Show 5 products per page
            page_number = request.GET.get('page')
            page_products = paginator.get_page(page_number)
            return render(request, 'search-result.html', {'products': page_products, 'product_count': product_count})   
    return render(request, 'search-result.html')


# customer store views
def store(request, category_slug=None):
    category = None
    products = None 
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        paginator = Paginator(products, 5)  # Show 5 products per page
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
        product_count = products.count()
        
    else:
        products = Product.objects.all().order_by('id')
        product_count = products.count()
        paginator = Paginator(products, 5)  # Show 5 products per page
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
    return render(request, 'store.html', {'products': page_products, 'product_count': product_count})




# customer product detail views
def product_detail(request , category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug )
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Product.DoesNotExist:
        single_product = None
    return render(request, 'product-detail.html', {'product': single_product, 'in_cart': in_cart})



# private function to get cart id
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# customer add tocart views
@login_required(login_url='signin')
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





# customer cart views
@login_required(login_url='signin')
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




# customer remove cart views
def remove_cart_item(request, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))

    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def increment_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.quantity += 1
    cart_item.save()

    return redirect('cart')


# customer remove cart views
def remove_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.delete()

    # If cart still has items → stay on cart page
    if CartItem.objects.filter(cart=cart).exists():
        return redirect('cart')
    return redirect('store')





# owner app views
@login_required
def owner_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    products = Product.objects.all()
    Categorys = Category.objects.all()
    Variants = Variant.objects.all()
    return render(request, 'owneradmin/dashboard.html', {'products': products, 'Categorys': Categorys, 'Variants': Variants})
@login_required
def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            brand_name=request.POST['brand_name'],
            product_name=request.POST['product_name'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            category_id=request.POST['category'],
            image=request.FILES['image'],
            description=request.POST['description'],
            variation=request.POST['variation'],
            size=request.POST['sizes'],
        )
        return redirect('owner_dashboard')

    categories = Category.objects.all()
    return render(request, 'owneradmin/add_product.html', {'categories': categories})

@login_required(login_url='signin')
def add_variant(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        Variant.objects.create(
            product_id=request.POST['product'],
            variant_category=request.POST['variant_category'],
            variant_value=request.POST['variant_value'],
            is_active=True if request.POST.get('is_active') else False,
        )
        messages.success(request, "Variant added successfully")
        return redirect('owner_dashboard')

    products = Product.objects.all()
    return render(request, 'owneradmin/add_variant.html', {
        'products': products
    })


@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.brand_name = request.POST['brand_name']
        product.product_name = request.POST['product_name']
        product.slug = slugify(request.POST['product_name'])
        product.description = request.POST['description']
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


def generate_unique_slug(model, name, instance_id=None):
    slug = slugify(name)
    unique_slug = slug
    counter = 1

    while model.objects.filter(slug=unique_slug).exclude(id=instance_id).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    return unique_slug


@login_required(login_url='signin')
def add_category(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        Category.objects.create(
            name=request.POST.get('name'),
            slug=generate_unique_slug(Category, request.POST.get('name')),
            description=request.POST.get('description', ''),
            cat_image=request.FILES.get('cat_image')
        )
        messages.success(request, "Category added successfully")
        return redirect('owner_dashboard')

    return render(request, 'owneradmin/add_category.html')  
        

@login_required(login_url='signin')
def edit_category(request, category_id):
    if not request.user.is_staff:
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if not name:
            messages.error(request, "Name is required")
            return redirect('edit_category', category_id=category.id)

        category.name = name
        category.slug = generate_unique_slug(Category, name, category.id)
        category.description = description

        if request.FILES.get('cat_image'):
            category.cat_image = request.FILES['cat_image']

        category.save()
        messages.success(request, "Category updated successfully")
        return redirect('owner_dashboard')

    return render(request, 'owneradmin/edit_category.html', {'category': category})
   
   
   
@login_required(login_url='signin')
def delete_category(request, category_id):
    if not request.user.is_staff:
        return redirect('home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('owner_dashboard')

    return render(request, 'owneradmin/delete_category.html', {'category': category})

