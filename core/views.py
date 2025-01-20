from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from .models import Product, Banner, Feature, Brand, SectionContent


def index(request):
    context = {
        'banners': Banner.objects.filter(active=True),
        'features': Feature.objects.all(),
        'brands': Brand.objects.all(),
        'section_contents': {
            'latest_products': SectionContent.objects.filter(section='latest_products').first(),
            'coming_products': SectionContent.objects.filter(section='coming_products').first(),
            'deals_week': SectionContent.objects.filter(section='deals_week').first(),
        }
    }
    
    # Adicione os produtos de cada seção ao contexto
    if context['section_contents']['latest_products']:
        context['latest_products'] = context['section_contents']['latest_products'].products.all()
    
    if context['section_contents']['coming_products']:
        context['coming_products'] = context['section_contents']['coming_products'].products.all()
    
    if context['section_contents']['deals_week']:
        context['deals_products'] = context['section_contents']['deals_week'].products.all()
    
    return render(request, 'core/index.html', context)

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

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)  
    related_products = Product.objects.exclude(id=id).order_by('?')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'core/single-product.html', context)
