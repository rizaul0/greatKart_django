from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from category.models import Category
from django.utils.text import slugify
from django.shortcuts import get_object_or_404  
# Create your views here.

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

