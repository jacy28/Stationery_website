from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart_view"), 
    path("cart/update/<int:item_id>/<str:action>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_cart, name="remove_cart"),
    path("payment/", views.payment, name='payment'),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('track_order/<int:order_id>/', views.track_order, name='track_order'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
]