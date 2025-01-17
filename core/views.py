from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages


def index(request):
    return render(request, 'core/index.html')

def cart(request):
    return render(request, 'core/cart.html')

def checkout(request):
    return render(request, 'core/checkout.html')

def contact(request):
    return render(request, 'core/contact.html')

def confirmation(request):
    return render(request, 'core/confirmation.html')

def category(request):
    return render(request, 'core/category.html')

def elements(request):
    return render(request, 'core/elements.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    return render(request, 'core/login.html')

def tracking(request):
    return render(request, 'core/tracking.html')

@login_required
def profile_view(request):
    return render(request, 'core/profile.html')

@login_required
def orders_view(request):
    return render(request, 'core/orders.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('core:index')

def register_view(request):
    return render(request, 'core/register.html')
