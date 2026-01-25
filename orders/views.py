from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import uuid

from cart.models import Cart, CartItem
from cart.views import _cart_id
from coupons.models import Coupon
from coupons.utils import calculate_coupon_discount
from orders.models import Order, OrderProduct
from orders.utils import generate_invoice_pdf
from utils.email import send_invoice_email_async
from .utils import generate_payu_hash
from django.core.mail import EmailMessage


# ========================= PLACE ORDER =========================
@login_required(login_url="signin")
def place_order(request):
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("store")

    total_price = sum(item.sub_total() for item in cart_items)
    coupon = None
    discount = Decimal("0.00")
    if "coupon_id" in request.session:
        coupon = Coupon.objects.filter(id=request.session["coupon_id"]).first()
        if coupon and coupon.is_valid():
            discount = calculate_coupon_discount(cart_items, coupon)

    tax = ((total_price - discount) * Decimal("0.09")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    grand_total = total_price - discount + tax

    # CREATE PENDING ORDER
    order = Order.objects.create(
        user=request.user,
        order_number=f"GK{int(timezone.now().timestamp())}",
        order_total=grand_total,
        tax=tax,
        coupon=coupon,
        discount=discount,
        status="New",
        is_ordered=False,
        ip=request.META.get("REMOTE_ADDR"),
    )

    request.session["pending_order_id"] = order.id

    return render(request, "place-order.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "discount": discount,
        "coupon": coupon,
        "tax": tax,
        "grand_total": grand_total,
        "order": order,
    })


# ========================= COD CONFIRM =========================
@login_required(login_url="signin")
def cod_confirm(request):
    order_id = request.session.get("pending_order_id")
    order = get_object_or_404(Order, id=order_id, is_ordered=False)

    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        color = ""
        size = ""
        for v in item.variation.all():
            if v.variant_category == "color":
                color = v.variant_value
            elif v.variant_category == "size":
                size = v.variant_value

        OrderProduct.objects.create(
            order=order,
            user=request.user,
            product=item.product,
            color=color,
            size=size,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )

        item.product.stock -= item.quantity
        item.product.save()

    order.payment_method = "COD"
    order.is_ordered = True
    order.status = "New"
    order.save()

    cart_items.delete()

    # SEND EMAIL
    order_products = OrderProduct.objects.filter(order=order)
    pdf = generate_invoice_pdf(order, order_products)

    send_invoice_email_async(order, pdf)

    del request.session["pending_order_id"]

    return redirect(f"/orders/order_complete/?order_id={order.id}")


# ========================= PAYU REDIRECT =========================
@login_required(login_url="signin")
def payu_redirect(request):
    if request.method != "POST":
        return redirect("cart")

    order_id = request.session.get("pending_order_id")
    order = get_object_or_404(Order, id=order_id, is_ordered=False)

    txnid = str(uuid.uuid4())[:20]

    payu_data = {
        "key": settings.PAYU_MERCHANT_KEY,
        "txnid": txnid,
        "amount": f"{order.order_total:.2f}",
        "productinfo": "GreatKart Order",
        "firstname": order.user.first_name.lower(),
        "email": order.user.email.lower(),
        "phone": order.user.phone,
        "udf1": "",
        "udf2": "",
        "udf3": "",
        "udf4": "",
        "udf5": "",
        "surl": request.build_absolute_uri("/orders/payu/success/"),
        "furl": request.build_absolute_uri("/orders/payu/failure/"),
    }

    payu_data["hash"] = generate_payu_hash(
        payu_data, settings.PAYU_MERCHANT_SALT
    )

    return render(request, "payu_redirect.html", {
        "payu_url": settings.PAYU_URL,
        "payu_data": payu_data,
    })


# ========================= PAYU SUCCESS =========================
@csrf_exempt
def payu_success(request):
    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    status = request.POST.get("status")
    txnid = request.POST.get("txnid")
    email = request.POST.get("email")

    if status != "success":
        return redirect("cart")

    order = Order.objects.filter(
        user__email=email,
        is_ordered=False
    ).last()

    if not order:
        return HttpResponse("Order not found", status=404)

    cart = Cart.objects.filter(user=order.user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        color = ""
        size = ""
        for v in item.variation.all():
            if v.variant_category == "color":
                color = v.variant_value
            elif v.variant_category == "size":
                size = v.variant_value

        OrderProduct.objects.create(
            order=order,
            user=order.user,
            product=item.product,
            color=color,
            size=size,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )

        item.product.stock -= item.quantity
        item.product.save()

    order.transaction_id = txnid
    order.payment_method = "PayU"
    order.is_ordered = True
    order.status = "New"
    order.save()

    cart_items.delete()

    # SEND EMAIL
    order_products = OrderProduct.objects.filter(order=order)
    pdf = generate_invoice_pdf(order, order_products)

    send_invoice_email_async(order, pdf)

    return redirect(f"/orders/order_complete/?order_id={order.id}")


# ========================= ORDER COMPLETE =========================
@login_required(login_url="signin")
def order_complete(request):
    order_id = request.GET.get("order_id")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        is_ordered=True
    )

    return render(request, "order_complete.html", {
        "order": order,
        "ordered_products": OrderProduct.objects.filter(order=order),

        "total_price": order.order_total,
        "tax": order.tax,
        "grand_total": order.order_total,
    })


# ========================= PAYU FAILURE =========================
@csrf_exempt
def payu_failure(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect("cart")
