from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.db.models import Avg
from .models import Product, Banner, Feature, Brand, SectionContent, Review


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
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'core/cart.html', context)

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

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Contagem de avaliações por estrela
    rating_counts = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating or 0,
        'rating_counts': rating_counts,
        'related_products': related_products,
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'core/single-product.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        
        # Inicializa o carrinho na sessão se não existir
        cart = request.session.get('cart', {})
        
        # Converte o product_id para string já que as chaves do dicionário na sessão são strings
        product_id_str = str(product_id)
        
        # Adiciona ou atualiza a quantidade do produto no carrinho
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity
            
        # Verifica se a quantidade não excede o estoque
        if cart[product_id_str] > product.stock_quantity:
            cart[product_id_str] = product.stock_quantity
            messages.warning(request, f'Quantidade ajustada para {product.stock_quantity} devido ao estoque disponível')
        
        # Salva o carrinho atualizado na sessão
        request.session['cart'] = cart
        messages.success(request, f'{product.name} adicionado ao carrinho!')
        
        return redirect('core:cart')
    
    return redirect('core:product_detail', product_id=product_id)

@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('review')
        
        if not rating or not comment:
            messages.error(request, 'Por favor, forneça uma avaliação e um comentário.')
            return redirect('core:product_detail', product_id=product_id)
        
        try:
            # Atualiza a avaliação existente ou cria uma nova
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            
            if created:
                messages.success(request, 'Avaliação adicionada com sucesso!')
            else:
                messages.success(request, 'Avaliação atualizada com sucesso!')
                
        except Exception as e:
            messages.error(request, 'Ocorreu um erro ao salvar sua avaliação.')
            
    return redirect('core:product_detail', product_id=product_id)

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if quantity <= 0:
            if product_id_str in cart:
                del cart[product_id_str]
                messages.success(request, f'{product.name} removido do carrinho!')
        else:
            if quantity > product.stock_quantity:
                quantity = product.stock_quantity
                messages.warning(request, f'Quantidade ajustada para {quantity} devido ao estoque disponível')
            
            cart[product_id_str] = quantity
            messages.success(request, f'Carrinho atualizado!')
        
        request.session['cart'] = cart
        
    return redirect('core:cart')

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            product = get_object_or_404(Product, id=product_id)
            del cart[product_id_str]
            request.session['cart'] = cart
            messages.success(request, f'{product.name} removido do carrinho!')
            
    return redirect('core:cart')
