from django.shortcuts import render

def test_view(request):
    return render(request, 'test.html')

def index(request):
    return render(request, 'core/base.html')

def cart(request):
    return render(request, 'core/cart.html')

def checkout(request):
    return render(request, 'core/checkout.html')

def confirmation(request):
    return render(request, 'core/confirmation.html')

def category(request):
    return render(request, 'core/category.html')

def blog(request):
    return render(request, 'core/blog.html')

def elements(request):
    return render(request, 'core/elements.html')

def login_view(request):
    return render(request, 'core/login.html')

def tracking(request):
    return render(request, 'core/tracking.html')
