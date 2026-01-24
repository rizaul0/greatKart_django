from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
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

