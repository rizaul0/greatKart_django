from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increment/<int:cart_item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrement/<int:cart_item_id>/', views.remove_cart_item, name='decrement_cart_item'),
    path('remove/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
]
