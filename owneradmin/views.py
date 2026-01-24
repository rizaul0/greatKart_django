from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from coupons.models import Coupon
from orders.models import Order, OrderProduct
from store.models import Product, Variant
from category.models import Category
# Create your views here.
# customer dashboard views



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



@login_required
def owner_products(request):
    if not request.user.is_staff:
        return redirect('home')

    products = Product.objects.select_related('category')
    return render(request, 'owneradmin/products.html', {
        'products': products
    })


@login_required
def owner_variants(request):
    if not request.user.is_staff:
        return redirect('home')

    variants = Variant.objects.select_related('product')
    return render(request, 'owneradmin/variants.html', {
        'variants': variants
    })


@login_required
def owner_orders(request):
    if not request.user.is_staff:
        return redirect('home')

    orders = Order.objects.select_related('user').order_by('-created_at')

    return render(request, 'owneradmin/orders.html', {
        'orders': orders
    })


@login_required
def owner_order_detail(request, id):
    if not request.user.is_staff:
        return redirect('home')

    order = get_object_or_404(Order, id=id)
    items = OrderProduct.objects.filter(order=order)

    return render(request, 'owneradmin/order_detail.html', {
        'order': order,
        'items': items
    })


@login_required
def owner_coupons(request):
    if not request.user.is_staff:
        return redirect('home')

    coupons = Coupon.objects.all().order_by('-valid_from')

    return render(request, 'owneradmin/coupons.html', {
        'coupons': coupons
    })


@login_required
def add_coupon(request):
    if not request.user.is_staff:
        return redirect('home')

    products = Product.objects.all()

    if request.method == "POST":
        coupon = Coupon.objects.create(
            code=request.POST.get('code').upper(),
            discount_percent=request.POST.get('discount_percent'),
            max_discount_amount=request.POST.get('max_discount_amount') or None,
            valid_from=request.POST.get('valid_from'),
            valid_to=request.POST.get('valid_to'),
            usage_limit=request.POST.get('usage_limit'),
            is_active=True if request.POST.get('is_active') else False,
        )

        product_ids = request.POST.getlist('products')
        coupon.products.set(product_ids)

        messages.success(request, "Coupon created successfully")
        return redirect('owner_coupons')

    return render(request, 'owneradmin/add_coupon.html', {
        'products': products
    })
    
@login_required
def edit_coupon(request, id):
    if not request.user.is_staff:
        return redirect('home')

    coupon = get_object_or_404(Coupon, id=id)
    products = Product.objects.all()

    if request.method == "POST":
        coupon.code = request.POST.get('code').upper()
        coupon.discount_percent = request.POST.get('discount_percent')
        coupon.max_discount_amount = request.POST.get('max_discount_amount') or None
        coupon.valid_from = request.POST.get('valid_from')
        coupon.valid_to = request.POST.get('valid_to')
        coupon.usage_limit = request.POST.get('usage_limit')
        coupon.is_active = True if request.POST.get('is_active') else False
        coupon.save()

        coupon.products.set(request.POST.getlist('products'))

        messages.success(request, "Coupon updated successfully")
        return redirect('owner_coupons')

    return render(request, 'owneradmin/edit_coupon.html', {
        'coupon': coupon,
        'products': products
    })
@login_required
def delete_coupon(request, id):
    if not request.user.is_staff:
        return redirect('home')

    coupon = get_object_or_404(Coupon, id=id)

    if request.method == "POST":
        coupon.delete()
        messages.success(request, "Coupon deleted successfully")
        return redirect('owner_coupons')

    return render(request, 'owneradmin/delete_coupon.html', {
        'coupon': coupon
    })

    