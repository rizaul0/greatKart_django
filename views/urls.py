from django.urls import path, include
from .views import home,product_detail,register,signin,dashboard,order_complete,place_order,search_results, store
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('signin/', signin, name='signin'),
    path('dashboard/', dashboard, name='dashboard'),
    path('order-complete/', order_complete, name='order_complete'),
    path('place-order/', place_order, name='place_order'),
    path('search-results/', search_results, name='search_results'),
    path('store/', store, name='store'),
    path('store/<slug:category_slug>/', store, name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>/', product_detail, name='product_detail'),
    
]