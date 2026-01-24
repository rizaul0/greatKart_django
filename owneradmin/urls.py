from django.urls import path
from . import views

urlpatterns = [
    path('', views.owner_dashboard, name='owner_dashboard'),
    path('products/', views.owner_products, name='owner_products'),
    path('variants/', views.owner_variants, name='owner_variants'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('orders/', views.owner_orders, name='owner_orders'),
    path('orders/<int:id>/', views.owner_order_detail, name='owner_order_detail'),

    path('coupons/', views.owner_coupons, name='owner_coupons'),
    path('add-coupon/', views.add_coupon, name='add_coupon'),
    path('add-variant/', views.add_variant, name='add_variant'),
    path('coupons/edit/<int:id>/', views.edit_coupon, name='edit_coupon'),
    path('coupons/delete/<int:id>/', views.delete_coupon, name='delete_coupon'),

]
