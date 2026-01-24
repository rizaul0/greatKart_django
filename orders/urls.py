from django.urls import path
from . import views

urlpatterns = [
    # Order flow
    path("place_order/", views.place_order, name="place_order"),
    path("order_complete/", views.order_complete, name="order_complete"),

    # COD
    path("cod/confirm/", views.cod_confirm, name="cod_confirm"),

    # PayU
    path("payu/", views.payu_redirect, name="payu_redirect"),
    path("payu/success/", views.payu_success, name="payu_success"),
    path("payu/failure/", views.payu_failure, name="payu_failure"),
]
