from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer
from apps.orders.models import Order
from apps.users.models import CustomUser

# REST API viewset
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

# Create payment intent (simulate payment process)
@require_POST
@login_required
def create_payment_intent(request):
    order_id = request.POST.get('order_id')
    payment_method = request.POST.get('payment_method', 'balance')
    
    if not order_id:
        return JsonResponse({'error': 'Missing order ID'}, status=400)
    
    try:
        order = Order.objects.get(id=order_id, buyer=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order does not exist or does not belong to current user'}, status=404)
    
    # Check order status
    if order.status != 'pending':
        return JsonResponse({'error': 'Can only pay for pending orders'}, status=400)
    
    # Check if already paid
    if order.payment_status == 'paid':
        return JsonResponse({'error': 'Order has already been paid'}, status=400)
    
    # Calculate order total amount
    total_amount = order.total_price
    
    # Check if balance is sufficient
    if payment_method == 'balance' and request.user.balance < total_amount:
        return JsonResponse({'error': 'Insufficient account balance', 'required': float(total_amount), 'balance': float(request.user.balance)}, status=400)
    
    # Create payment record
    try:
        with transaction.atomic():
            # Deduct balance
            if payment_method == 'balance':
                request.user.balance -= total_amount
                request.user.save()
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                order=order,
                amount=total_amount,
                payment_method=payment_method,
                status='completed'
            )
            
            # Update order status
            order.status = 'paid'
            order.payment_status = 'paid'
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful',
                'payment_id': payment.id,
                'amount': float(total_amount),
                'order_id': order.id
            })
    except Exception as e:
        return JsonResponse({'error': f'Payment processing failed: {str(e)}'}, status=500)

# View payment history
@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payment_history.html', {'payments': payments})

# Recharge balance
@login_required
def recharge_balance(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount', '0')
        
        try:
            # Convert input to Decimal type to match user balance field type
            from decimal import Decimal
            amount = Decimal(amount_str)
            
            if amount <= 0:
                messages.error(request, 'Recharge amount must be greater than 0')
                return redirect('recharge_balance')
            
            # Simulate recharge process (should integrate with payment gateway in production)
            with transaction.atomic():
                request.user.balance += amount
                request.user.save()
                
                messages.success(request, f'Successfully recharged £{amount}')
                return redirect('account_settings')
        except ValueError:
            messages.error(request, 'Please enter a valid amount')
            return redirect('recharge_balance')
    
    return render(request, 'recharge_balance.html')