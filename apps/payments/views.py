from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse  
from .models import RefundRequest, Payment
from .forms import RefundRequestForm, AdminRefundResponseForm
from apps.orders.models import Order
from notifications.signals import notify
import time  
from decimal import Decimal, InvalidOperation  # Add InvalidOperation import

@login_required
def request_refund(request, order_id):
    """Buyer requests a refund"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Check if the order is eligible for refund
    if not order.can_refund():
        messages.error(request, "This order is not eligible for a refund")
        return redirect('order_detail', order_id=order_id)
    
    # Check if there's already a refund request
    if RefundRequest.objects.filter(order=order, status__in=['pending', 'approved']).exists():
        messages.error(request, "There is already a refund request in process for this order")
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            refund_request = form.save(commit=False)
            refund_request.order = order
            refund_request.user = request.user
            
            # Verify refund amount doesn't exceed order total
            if refund_request.amount > order.total_price:
                messages.error(request, "Refund amount cannot exceed the order total")
                return render(request, 'request_refund.html', {'form': form, 'order': order})
            
            refund_request.save()
            
            # Notify seller
            for item in order.items.all():
                notify.send(
                    request.user,
                    recipient=item.product.seller,
                    verb='requested_refund',
                    target=refund_request,
                    description=f'Buyer {request.user.username} requested a refund for order #{order.id}'
                )
            
            messages.success(request, "Refund request submitted, waiting for seller review")
            return redirect('view_refund_request', request_id=refund_request.id)
    else:
        # Default refund amount is the order total
        form = RefundRequestForm(initial={'amount': order.total_price})
    
    return render(request, 'request_refund.html', {'form': form, 'order': order})

@login_required
def view_refund_request(request, request_id):
    """View refund request details"""
    refund_request = get_object_or_404(RefundRequest, id=request_id)
    order = refund_request.order
    
    # Verify user permissions (only buyer and seller can view)
    is_buyer = order.buyer == request.user
    is_seller = any(item.product.seller == request.user for item in order.items.all())
    
    if not (is_buyer or is_seller or request.user.is_staff):
        messages.error(request, "You don't have permission to view this refund request")
        return redirect('home')
    
    return render(request, 'view_refund_request.html', {
        'refund_request': refund_request,
        'order': order,
        'is_buyer': is_buyer,
        'is_seller': is_seller,
        'is_staff': request.user.is_staff
    })

@login_required
def process_refund(request, request_id):
    """Process refund request"""
    refund_request = get_object_or_404(RefundRequest, id=request_id)
    order = refund_request.order
    
    # Verify user is seller or admin
    is_seller = any(item.product.seller == request.user for item in order.items.all())
    if not (is_seller or request.user.is_staff):
        messages.error(request, "You don't have permission to process this refund")
        return redirect('home')
    
    # Verify refund request status
    if refund_request.status != 'pending':
        messages.error(request, "This refund request has already been processed")
        return redirect('view_refund_request', request_id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        # Update refund request
        refund_request.admin_notes = admin_notes
        
        if action == 'approve':
            # Approve refund
            refund_request.status = 'approved'
            refund_request.save()
            
            # Process refund payment
            process_refund_payment(refund_request)
            
            # Update order status if needed
            if order.status != 'refunded':
                order.status = 'refunded'
                order.save()
            
            # Notify buyer
            notify.send(
                request.user,
                recipient=refund_request.user,
                verb='approved refund',
                target=refund_request,
                description=f'Your refund request for order #{order.id} has been approved'
            )
            
            messages.success(request, "Refund has been approved and processed")
        
        elif action == 'reject':
            # Reject refund
            refund_request.status = 'rejected'
            refund_request.save()
            
            # Notify buyer
            notify.send(
                request.user,
                recipient=refund_request.user,
                verb='rejected refund',
                target=refund_request,
                description=f'Your refund request for order #{order.id} has been rejected'
            )
            
            messages.success(request, "Refund has been rejected")
        
        return redirect('view_refund_request', request_id=request_id)
    
    return render(request, 'process_refund.html', {
        'refund_request': refund_request,
        'order': order
    })

def process_refund_payment(refund_request):
    """Process refund payment logic"""
    order = refund_request.order
    buyer = order.buyer
    
    # Create refund payment record
    payment = Payment.objects.create(
        user=buyer,
        order=order,
        amount=refund_request.amount,
        payment_method='refund',
        status='completed',
        transaction_id=f'REF-{refund_request.id}'
    )
    
    # Update buyer balance
    buyer.balance += refund_request.amount
    buyer.save()
    
    # Update refund request status
    refund_request.status = 'completed'
    refund_request.save()
    
    return payment

@login_required
def my_refund_requests(request):
    """View my refund requests list"""
    # Get user's refund requests as buyer
    buyer_requests = RefundRequest.objects.filter(
        user=request.user
    ).select_related('order').order_by('-created_at')
    
    # Get user's refund requests as seller
    seller_requests = RefundRequest.objects.filter(
        order__items__product__seller=request.user
    ).select_related('order').distinct().order_by('-created_at')
    
    return render(request, 'my_refund_requests.html', {
        'buyer_requests': buyer_requests,
        'seller_requests': seller_requests
    })


# Ensure this function is defined in the file
def create_payment_intent(request):
    """
    Create payment intent
    """
    # Temporary implementation, can be improved as needed
    return JsonResponse({'status': 'success', 'message': 'Payment intent created successfully'})

@login_required
def payment_history(request):
    """
    View payment history
    """
    payments = Payment.objects.filter(user=request.user).select_related('order').order_by('-created_at')
    return render(request, 'payment_history.html', {'payments': payments})

@login_required
def recharge_balance(request):
    """
    Recharge account balance
    """
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'credit_card')
        
        # Validate amount
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('recharge_balance')
        except (ValueError, InvalidOperation):
            messages.error(request, "Please enter a valid amount.")
            return redirect('recharge_balance')
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_method=payment_method,
            payment_type='recharge',
            status='completed',  # Assume payment is successful for demo
            description=f"Account balance recharge"
        )
        
        # Update user balance
        request.user.balance += amount
        request.user.save()
        
        messages.success(request, f"Successfully recharged £{amount} to your account.")

        return redirect('payment_history')
    
    return render(request, 'recharge_balance.html')