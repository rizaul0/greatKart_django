from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('store/', views.store, name='store'),
    path('store/search/', views.search_results, name='search_results'),

    path('store/<slug:category_slug>/', views.store, name='products_by_category'),
    path(
        'store/<slug:category_slug>/<slug:product_slug>/',
        views.product_detail,
        name='product_detail'
    ),
    path('dashboard/', views.dashboard, name='dashboard'),
]
