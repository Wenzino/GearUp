from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('category/', views.category, name='category'),
    path('blog/', views.blog, name='blog'),
    path('elements/', views.elements, name='elements'),
    path('login/', views.login_view, name='login'),
    path('tracking/', views.tracking, name='tracking'),
] 