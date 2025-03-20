from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import CartItem
from .serializers import CartItemSerializer
from apps.products.models import Product
from apps.orders.models import Order, OrderItem

# REST API viewset
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response({"message": "Cart has been cleared"})

# Add to cart
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('product_detail', pk=product_id)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if it's user's own product
        if product.seller == request.user:
            messages.error(request, 'You cannot purchase your own product')
            return redirect('product_detail', pk=product_id)
        
        # Check if product already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # If already exists, update quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.title} in your cart, current quantity: {cart_item.quantity}')
        else:
            messages.success(request, f'Added {product.title} to your cart')
        
        # Check if there's a next parameter
        next_url = request.POST.get('next', 'view_cart')
        return redirect(next_url)
    
    return redirect('home')

# View cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    # Calculate total price
    total_price = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    
    return render(request, 'cart.html', context)

# Remove item from cart
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    
    messages.success(request, f'Removed {product_title} from your cart')
    return redirect('view_cart')

# Update cart item quantity
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            # If quantity is 0 or negative, remove the item
            product_title = cart_item.product.title
            cart_item.delete()
            messages.success(request, f'Removed {product_title} from your cart')
        else:
            # Update quantity
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'Updated {cart_item.product.title} quantity to {quantity}')
        
        return redirect('view_cart')
    
    return redirect('view_cart')

# Buy now functionality
@login_required
def buy_now(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than 0')
            return redirect('product_detail', pk=product_id)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if it's user's own product
        if product.seller == request.user:
            messages.error(request, 'You cannot purchase your own product')
            return redirect('product_detail', pk=product_id)
        
        # Create a temporary cart item
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity = quantity  # Override existing quantity
            cart_item.save()
        
        # Redirect to checkout page with buy_now parameter
        return redirect(f"{reverse('checkout')}?buy_now={product_id}")
    
    return redirect('home')
