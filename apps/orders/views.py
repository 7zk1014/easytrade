from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.cart.models import CartItem
from apps.products.models import Product
from apps.payments.models import Payment
from apps.reviews.models import Review

# Viewset for Order, showing orders for the logged-in buyer
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({"message": "Order has been cancelled"})
        return Response({"error": "Only pending orders can be cancelled"}, status=400)

# Checkout functionality
@login_required
def checkout(request):
    # Check if it's a buy now purchase
    buy_now_product_id = request.GET.get('buy_now')
    
    if buy_now_product_id:
        # Buy now mode
        try:
            product = Product.objects.get(id=buy_now_product_id)
            cart_item = CartItem.objects.get(user=request.user, product=product)
            cart_items = [cart_item]
            total_price = cart_item.total_price
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Product does not exist or has been removed from cart')
            return redirect('home')
    else:
        # Regular cart checkout
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('view_cart')
        
        total_price = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        payment_method = request.POST.get('payment_method', 'balance')
        notes = request.POST.get('notes', '')
        
        # Check if balance is sufficient
        if payment_method == 'balance' and request.user.balance < total_price:
            messages.error(request, 'Your account balance is insufficient')
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'user_balance': request.user.balance
            })
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                buyer=request.user,
                status='pending',
                shipping_address=shipping_address,
                payment_method=payment_method,
                notes=notes
            )
            
            # Add order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # If paying with balance, deduct immediately and update order status
            if payment_method == 'balance':
                # Deduct balance
                request.user.balance -= total_price
                request.user.save()
                
                # Create payment record
                Payment.objects.create(
                    user=request.user,
                    order=order,
                    amount=total_price,
                    payment_method=payment_method,
                    status='completed'
                )
                
                # Update order status
                order.status = 'paid'
                order.payment_status = 'paid'
                order.save()
                
                # Clear cart (if buy now, only delete related product)
                if buy_now_product_id:
                    CartItem.objects.filter(user=request.user, product_id=buy_now_product_id).delete()
                else:
                    CartItem.objects.filter(user=request.user).delete()
                
                messages.success(request, 'Order payment successful!')
                return redirect('order_detail', order_id=order.id)
            
            # Other payment methods (not implemented)
            messages.info(request, 'Please complete payment')
            return redirect('order_detail', order_id=order.id)
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_balance': request.user.balance,
        'is_buy_now': bool(buy_now_product_id)
    })

# Order history
@login_required
def order_history(request):

    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

# Order details
@login_required
def order_detail(request, order_id):
    # 修改这里：将 user 改为 buyer
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    order_items = order.items.all()
    
    # Create a dictionary to track which products the user has reviewed
    user_reviews = {}
    for item in order_items:
        user_reviews[item.product.id] = Review.objects.filter(
            product=item.product, 
            reviewer=request.user
        ).exists()
    
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'user_reviews': user_reviews
    })

# Cancel order
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Can only cancel pending orders
    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be cancelled')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # If already paid, refund balance
        if order.payment_status == 'paid' and order.payment_method == 'balance':
            with transaction.atomic():
                # Refund balance
                total_price = order.total_price
                request.user.balance += total_price
                request.user.save()
                
                # Update payment record
                payment = Payment.objects.filter(order=order, status='completed').first()
                if payment:
                    payment.status = 'refunded'
                    payment.save()
                
                # Update order status
                order.status = 'cancelled'
                order.payment_status = 'refunded'
                order.save()
                
                messages.success(request, f'Order cancelled, £{total_price} has been refunded to your account')
        else:
            # Unpaid orders can be cancelled directly
            order.status = 'cancelled'
            order.save()
            messages.success(request, 'Order has been cancelled')
    
    return redirect('order_detail', order_id=order.id)

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    if request.method == 'POST':
        # ... 支付处理逻辑 ...
        
        if payment_successful:
            # 更新订单状态
            order.status = 'paid'
            order.save()
            
            # 将订单中的所有商品标记为已售出
            for item in order.items.all():
                product = item.product
                product.status = 'sold'
                product.save()
            
            messages.success(request, "Payment successful! Your order has been confirmed.")
            return redirect('order_detail', order_id=order.id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order

@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {
        'orders': orders
    })
