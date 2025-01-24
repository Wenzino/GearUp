from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('category/', views.category, name='category'),
    path('elements/', views.elements, name='elements'),
    path('tracking/', views.tracking, name='tracking'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.orders_view, name='orders'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-payment-intent/', views.create_stripe_payment_intent, name='create_payment_intent'),
    path('create-paypal-payment/', views.create_paypal_payment, name='create_paypal_payment'),
    path('execute-paypal-payment/', views.execute_paypal_payment, name='execute_paypal_payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('checkout/failed/', views.payment_failed, name='payment_failed'),
] 

