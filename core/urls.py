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
] 