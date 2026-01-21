from django.urls import path
from django.contrib.auth import views as auth_views
from views import views
from accounts import views
from .views import add_category, add_product, add_to_cart, add_variant, delete_product, edit_product, home, increment_cart_item, logout_user, owner_dashboard,product_detail,register, remove_cart, remove_cart_item,signin,dashboard,order_complete,place_order,search_results, store,cart, edit_category, delete_category, forgot_password, reset_password
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('signin/', signin, name='signin'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', reset_password, name='reset_password'),

    path('logout/', logout_user, name='logout'),
    

    path('dashboard/', dashboard, name='dashboard'),
    path('order-complete/', order_complete, name='order_complete'),
    path('place-order/', place_order, name='place_order'),
    path('search-results/', search_results, name='search_results'),
    path('store/', store, name='store'),
    path('store/<slug:category_slug>/', store, name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>/', product_detail, name='product_detail'),
    path('store/<slug:brand>/', store, name='products_by_brand'),
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/',remove_cart, name='remove_cart'),
    path('cart/remove_item/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),
    path('cart/increment/<int:cart_item_id>/', increment_cart_item, name='increment_cart_item'),



    
    
    
    
    # owner app urls
    path('owneradmin/', owner_dashboard, name='owner_dashboard'),
    path('owneradmin/add-category/', add_category, name='add_category'),
    path('owneradmin/edit-category/<int:category_id>/', edit_category, name='edit_category'),
    path('owneradmin/delete-category/<int:category_id>/', delete_category, name='delete_category'),


    
    path('owneradmin/add-product/', add_product, name='add_product'),
    path('owneradmin/edit-product/<int:id>/', edit_product, name='edit_product'),
    path('owneradmin/delete-product/<int:id>/', delete_product, name='delete_product'),
    path('owneradmin/add-variant/', add_variant, name='add_variant'),

]

