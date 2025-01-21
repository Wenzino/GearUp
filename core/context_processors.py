def cart_count(request):
    cart = request.session.get('cart', {})
    # Conta apenas o número de itens diferentes (chaves) no carrinho
    total_items = len(cart.keys())
    return {'cart_count': total_items} 