from random import random
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages, auth 
from django.shortcuts import render, redirect
from accounts.models import Account, PasswordResetToken
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
import random
from utils.email import send_email_async
from cart.models import Cart, CartItem
from orders.models import Order
from store.models import Product, Variant


# Create your views here.
# customer auth views
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        street = request.POST['street']
        house = request.POST['house']
        confirm_password = request.POST['confirm_password']
        city = request.POST['city']
        zip = request.POST['zip']
        country = request.POST['country']
        gender = request.POST.get('gender', 'M')
        phone = request.POST['phone']

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
        user.street = street
        user.house = house
        user.country = country
        user.gender = gender
        user.zip = zip
        user.phone = phone
        user.is_active = True   # customer account
        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('signin')

    return render(request, 'register.html')



def merge_session_cart_to_user_with_key(session_key, user):
    try:
        session_cart = Cart.objects.get(cart_id=session_key)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(
        cart_id=f"user_{user.id}",
        defaults={'user': user}
    )

    # ✅ ensure user is set
    if user_cart.user is None:
        user_cart.user = user
        user_cart.save()

    for item in CartItem.objects.filter(cart=session_cart):
        existing_items = CartItem.objects.filter(
            cart=user_cart,
            product=item.product
        )

        merged = False
        for existing in existing_items:
            if list(existing.variation.all()) == list(item.variation.all()):
                existing.quantity += item.quantity
                existing.save()
                merged = True
                break

        if not merged:
            item.cart = user_cart
            item.save()

    session_cart.delete()

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
        send_email_async(
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
           
            recipients=[user.email],
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
        old_session_key = request.session.session_key
        login(request, user)
         # secure session
        merge_session_cart_to_user_with_key(old_session_key, user)
        request.session.cycle_key()
        # Update last_login
        user.last_login = now()
        user.save()
        login_time = timezone.localtime(timezone.now())
        # Send successful login email
        send_email_async(
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
            
            recipients=user.email,
            fail_silently=False,
        )

        # Clean session
        request.session.pop('login_otp', None)
        request.session.pop('login_email', None)


        messages.success(request, "Login successful")
        return redirect('home')

    # STEP 0 — NORMAL GET REQUEST
    return render(request, 'signin.html')



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

        send_email_async(
            subject="Reset your GreatKart password",
            message=f"Click the link to reset your password:\n\n{reset_link}",
            
            recipients=email,
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


@login_required
def edit_address(request):
    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.phone = request.POST.get("phone")
        
        user.house = request.POST.get("house")
        user.street = request.POST.get("street")
        user.city = request.POST.get("city")
        user.state = request.POST.get("state")
        user.zip = request.POST.get("zip")
        user.country = request.POST.get("country")

        user.save()
        messages.success(request, "Address updated successfully.")
        return redirect("dashboard")

    return render(request, "auth/edit_address.html", {
        "user": user
    })


# customer auth views
def logout_user(request):
    logout(request)
    return redirect('home')



@login_required(login_url='signin')
def dashboard(request):
    orders = (
        Order.objects
        .filter(user=request.user, is_ordered=True)
        .select_related('coupon')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    return render(request, 'dashboard.html', {
        'orders': orders
    })

