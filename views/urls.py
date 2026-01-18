from django.urls import path, include

from views import views
from accounts import views
from .views import add_category, add_product, add_to_cart, delete_product, edit_product, home, logout_user, owner_dashboard,product_detail,register, remove_cart, remove_cart_item,signin,dashboard,order_complete,place_order,search_results, store,cart, edit_category, delete_category
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('signin/', signin, name='signin'),
    path('logout/', logout_user, name='logout'),

    path('dashboard/', dashboard, name='dashboard'),
    path('order-complete/', order_complete, name='order_complete'),
    path('place-order/', place_order, name='place_order'),
    path('search-results/', search_results, name='search_results'),
    path('store/', store, name='store'),
    path('store/<slug:category_slug>/', store, name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>/', product_detail, name='product_detail'),
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_cart_item, name='remove_cart_item'),
    path('cart/remove_cart/<int:product_id>/', remove_cart, name='remove_cart'),
    
    
    
    
    # owner app urls
     path('owneradmin/add-category/', add_category, name='add_category'),
    path('owneradmin/edit-category/<int:category_id>/', edit_category, name='edit_category'),
    path('owneradmin/delete-category/<int:category_id>/', delete_category, name='delete_category'),


    path('owneradmin/', owner_dashboard, name='owner_dashboard'),
    path('owneradmin/add-product/', add_product, name='add_product'),
    path('owneradmin/edit-product/<int:id>/', edit_product, name='edit_product'),
    path('owneradmin/delete-product/<int:id>/', delete_product, name='delete_product'),
]