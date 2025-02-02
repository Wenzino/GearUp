from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Avg
from .models import Product, Banner, Feature, Brand, SectionContent, Review, Order, OrderItem, BillingAddress
from decimal import Decimal
import stripe
from django.conf import settings
from django.http import JsonResponse
import paypalrestsdk
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.urls import reverse
from django.utils.translation import get_language_from_request
from django_countries import countries
from django.db.utils import IntegrityError


stripe.api_key = settings.STRIPE_SECRET_KEY

# Configurar o PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox ou live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

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

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('core:cart')
    
    cart_items = []
    subtotal = 0
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        item_subtotal = product.price * quantity
        subtotal += item_subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': item_subtotal
        })
    
    shipping_cost = Decimal('2.00')  # Valor fixo por enquanto
    total = subtotal + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'countries': countries,
        'default_country': request.META.get('HTTP_CF_IPCOUNTRY') or None,
        'default_address': {
            'address': request.user.billing_address.address if hasattr(request.user, 'billing_address') else '',
            'city': request.user.billing_address.city if hasattr(request.user, 'billing_address') else '',
            'state': request.user.billing_address.state if hasattr(request.user, 'billing_address') else '',
            'postal_code': request.user.billing_address.postal_code if hasattr(request.user, 'billing_address') else '',
            'country': request.user.billing_address.country if hasattr(request.user, 'billing_address') else '',
        }
    }
    
    return render(request, 'core/checkout.html', context)

def calculate_total(cart):
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        total += product.price * quantity
    return total

@login_required
def create_stripe_payment_intent(request):
    try:
        cart = request.session.get('cart', {})
        total = calculate_total(cart)  # Você precisa implementar esta função
        
        # Criar PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # Stripe trabalha com centavos
            currency='eur',
            metadata={'integration_check': 'accept_a_payment'}
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)

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
    if request.method == 'POST':
        try:
            # Validação dos campos obrigatórios
            required_fields = {
                'address': 'Endereço',
                'city': 'Cidade',
                'state': 'Estado',
                'postal_code': 'CEP',
                'country': 'País'
            }
            
            missing_fields = [name for field, name in required_fields.items() if not request.POST.get(field)]
            if missing_fields:
                messages.error(request, f'Campos obrigatórios faltando: {", ".join(missing_fields)}')
                return redirect('core:profile')

            # Atualizar dados do usuário
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()

            # Atualizar endereço de cobrança
            billing_address, _ = BillingAddress.objects.get_or_create(user=user)
            billing_address.address = request.POST.get('address', '')
            billing_address.city = request.POST.get('city', '')
            billing_address.state = request.POST.get('state', '')
            billing_address.postal_code = request.POST.get('postal_code', '')
            billing_address.country = request.POST.get('country', '')
            billing_address.save()

            # Alterar senha se os campos foram preenchidos
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if old_password and new_password1 and new_password2:
                if user.check_password(old_password):
                    if new_password1 == new_password2:
                        user.set_password(new_password1)
                        user.save()
                        messages.success(request, 'Senha alterada com sucesso!')
                    else:
                        messages.error(request, 'As novas senhas não coincidem')
                else:
                    messages.error(request, 'Senha atual incorreta')

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:profile')

        except IntegrityError as e:
            messages.error(request, 'Erro ao salvar endereço. Verifique os dados informados.')
            return redirect('core:profile')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
            return redirect('core:profile')

    # Adicionar países ao contexto
    context = {
        'countries': countries,
        'user': request.user
    }
    return render(request, 'core/profile.html', context)

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'core/orders.html', {'orders': orders})

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

@login_required
def create_paypal_payment(request):
    try:
        data = json.loads(request.body) if request.body else {}
        cart = request.session.get('cart', {})
        cart_items = []
        subtotal = Decimal('0.00')
        
        # Calcula o total e prepara os itens
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=int(product_id))
            item_total = product.price * quantity
            subtotal += item_total
            
            cart_items.append({
                "name": product.name,
                "sku": f"PROD-{product.id}",
                "price": str(product.price),
                "currency": "EUR",
                "quantity": quantity
            })

        shipping_cost = Decimal('10.00')
        total = subtotal + shipping_cost

        # Criar o pagamento PayPal com informações de envio
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal",
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('core:execute_paypal_payment')),
                "cancel_url": request.build_absolute_uri(reverse('core:payment_failed'))
            },
            "transactions": [{
                "item_list": {
                    "items": cart_items,
                    "shipping_address": {
                        "recipient_name": f"{data.get('first_name', '')} {data.get('last_name', '')}",
                        "line1": data.get('address', ''),
                        "city": data.get('city', ''),
                        "state": data.get('state', ''),
                        "postal_code": data.get('postal_code', ''),
                        "country_code": data.get('country', ''),
                    } if all(data.get(k) for k in ['address', 'city', 'state', 'postal_code', 'country']) else None
                },
                "amount": {
                    "total": str(total),
                    "currency": "EUR",
                    "details": {
                        "subtotal": str(subtotal),
                        "shipping": str(shipping_cost)
                    }
                },
                "description": "Compra na Gear Up Store"
            }]
        })

        if payment.create():
            request.session['paypal_payment_id'] = payment.id
            
            # Encontra o link de aprovação
            approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
            
            if approval_url:
                return JsonResponse({
                    'success': True,
                    'approval_url': approval_url
                })
            
        return JsonResponse({
            'success': False,
            'error': 'Falha ao criar pagamento PayPal'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def execute_paypal_payment(request):
    payment_id = request.session.get('paypal_payment_id')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, 'Informações de pagamento inválidas.')
        return redirect('core:payment_failed')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        try:
            # Recupera informações do carrinho
            cart = request.session.get('cart', {})
            subtotal = Decimal('0.00')
            
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=int(product_id))
                subtotal += product.price * quantity

            shipping_cost = Decimal('10.00')
            total = subtotal + shipping_cost

            # Cria o pedido
            order = Order.objects.create(
                user=request.user,
                status='paid',
                payment_id=payment_id,
                shipping_address=payment.transactions[0].item_list.shipping_address.line1 if hasattr(payment.transactions[0], 'item_list') and hasattr(payment.transactions[0].item_list, 'shipping_address') else '',
                shipping_city=payment.transactions[0].item_list.shipping_address.city if hasattr(payment.transactions[0], 'item_list') and hasattr(payment.transactions[0].item_list, 'shipping_address') else '',
                shipping_state=payment.transactions[0].item_list.shipping_address.state if hasattr(payment.transactions[0], 'item_list') and hasattr(payment.transactions[0].item_list, 'shipping_address') else '',
                shipping_zip=payment.transactions[0].item_list.shipping_address.postal_code if hasattr(payment.transactions[0], 'item_list') and hasattr(payment.transactions[0].item_list, 'shipping_address') else '',
                shipping_country=payment.transactions[0].item_list.shipping_address.country_code if hasattr(payment.transactions[0], 'item_list') and hasattr(payment.transactions[0].item_list, 'shipping_address') else '',
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=total
            )

            # Cria os itens do pedido
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=int(product_id))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            # Limpa o carrinho e a sessão do PayPal
            request.session['cart'] = {}
            del request.session['paypal_payment_id']
            
            messages.success(request, 'Pagamento realizado com sucesso!')
            return redirect('core:payment_success')

        except Exception as e:
            messages.error(request, f'Erro ao processar o pedido: {str(e)}')
            return redirect('core:payment_failed')
    else:
        messages.error(request, 'Erro ao executar o pagamento.')
        return redirect('core:payment_failed')

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def process_payment(request):
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        # Verifica se o país foi enviado
        shipping_country = data.get('country')
        if not shipping_country:
            return JsonResponse({
                'error': 'País é obrigatório'
            }, status=400)

        # Calcular total do carrinho
        cart = request.session.get('cart', {})
        subtotal = Decimal('0.00')
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=int(product_id))
            subtotal += product.price * quantity
        shipping_cost = Decimal('10.00')  # Exemplo fixo
        total = subtotal + shipping_cost

        # Criar pedido
        order = Order.objects.create(
            user=request.user,
            status='pending',
            shipping_address=data.get('address'),
            shipping_city=data.get('city'),
            shipping_state=data.get('state'),
            shipping_zip=data.get('postal_code'),
            shipping_country=shipping_country,  # Usa o país do formulário
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total
        )

        # Criar itens do pedido
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=int(product_id))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        # Processar pagamento com Stripe
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total * 100),  # Stripe usa centavos
                currency='usd',
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                return_url=request.build_absolute_uri(reverse('core:payment_success')),
            )

            if payment_intent.status == 'succeeded':
                # Atualizar pedido
                order.status = 'paid'
                order.payment_id = payment_intent.id
                order.save()

                # Limpar carrinho
                request.session['cart'] = {}
                request.session.modified = True

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('core:payment_success')
                })
            elif payment_intent.status == 'requires_action':
                return JsonResponse({
                    'requires_action': True,
                    'payment_intent_client_secret': payment_intent.client_secret
                })
            else:
                order.status = 'failed'
                order.save()
                return JsonResponse({
                    'error': 'Pagamento falhou'
                }, status=400)

        except stripe.error.StripeError as e:
            order.status = 'failed'
            order.save()
            return JsonResponse({
                'error': str(e)
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@login_required
def payment_success(request):
    return render(request, 'core/payment_success.html')

@login_required
def payment_failed(request):
    return render(request, 'core/payment_failed.html')

