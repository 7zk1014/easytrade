from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Dispute, DisputeMessage
from .serializers import DisputeSerializer, DisputeMessageSerializer
from apps.orders.models import Order

# API ViewSets
class DisputeViewSet(viewsets.ModelViewSet):
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Dispute.objects.all().select_related('order', 'complainant')
        return Dispute.objects.filter(complainant=user).select_related('order', 'complainant')
    
    def perform_create(self, serializer):
        serializer.save(complainant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        
        # Only staff or the seller of the order can resolve disputes
        if not (request.user.is_staff or request.user == dispute.order.seller):
            return Response({"error": "You don't have permission to resolve this dispute"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        resolution = request.data.get('resolution', '')
        if not resolution:
            return Response({"error": "Resolution is required"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        dispute.status = 'resolved'
        dispute.resolution = resolution
        dispute.resolved_by = request.user
        dispute.resolved_at = timezone.now()
        dispute.save()
        
        return Response({"message": "Dispute resolved successfully"})
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        dispute = self.get_object()
        
        # Only the complainant can escalate their own dispute
        if request.user != dispute.complainant:
            return Response({"error": "You can only escalate your own disputes"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        if dispute.status == 'resolved':
            dispute.status = 'escalated'
            dispute.save()
            return Response({"message": "Dispute escalated to admin"})
        
        return Response({"error": "Only resolved disputes can be escalated"}, 
                       status=status.HTTP_400_BAD_REQUEST)

class DisputeMessageViewSet(viewsets.ModelViewSet):
    serializer_class = DisputeMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DisputeMessage.objects.all()
        
        # Users can only see messages for disputes they're involved in
        return DisputeMessage.objects.filter(
            dispute__complainant=user
        ) | DisputeMessage.objects.filter(
            dispute__order__seller=user
        )
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

# Web Views
@login_required
def dispute_list(request):
    if request.user.is_staff:
        disputes = Dispute.objects.all().order_by('-created_at')
    else:
        # Regular users see disputes for orders they bought or sold
        disputes = Dispute.objects.filter(
            complainant=request.user
        ) | Dispute.objects.filter(
            order__seller=request.user
        ).distinct().order_by('-created_at')
    
    return render(request, 'disputes/dispute_list.html', {'disputes': disputes})

@login_required
def dispute_detail(request, dispute_id):
    # Staff can view all disputes, users can only view their own
    if request.user.is_staff:
        dispute = get_object_or_404(Dispute, id=dispute_id)
    else:
        dispute = get_object_or_404(
            Dispute, 
            id=dispute_id,
            complainant=request.user
        ) | get_object_or_404(
            Dispute,
            id=dispute_id,
            order__seller=request.user
        )
    
    # Handle new messages
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            DisputeMessage.objects.create(
                dispute=dispute,
                sender=request.user,
                message=message_text
            )
            messages.success(request, 'Message sent successfully')
            return redirect('dispute_detail', dispute_id=dispute.id)
    
    dispute_messages = dispute.messages.all().order_by('created_at')
    
    return render(request, 'disputes/dispute_detail.html', {
        'dispute': dispute,
        'dispute_messages': dispute_messages
    })

@login_required
def create_dispute(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Check if dispute already exists
    if Dispute.objects.filter(order=order, complainant=request.user).exists():
        messages.error(request, 'You already have an open dispute for this order')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if reason:
            dispute = Dispute.objects.create(
                order=order,
                complainant=request.user,
                reason=reason
            )
            messages.success(request, 'Dispute created successfully')
            return redirect('dispute_detail', dispute_id=dispute.id)
        else:
            messages.error(request, 'Please provide a reason for the dispute')
    
    return render(request, 'disputes/create_dispute.html', {'order': order})

@login_required
def resolve_dispute(request, dispute_id):
    # Only staff or the seller can resolve disputes
    if request.user.is_staff:
        dispute = get_object_or_404(Dispute, id=dispute_id)
    else:
        dispute = get_object_or_404(Dispute, id=dispute_id, order__seller=request.user)
    
    if dispute.status in ['resolved', 'closed']:
        messages.error(request, 'This dispute is already resolved or closed')
        return redirect('dispute_detail', dispute_id=dispute.id)
    
    if request.method == 'POST':
        resolution = request.POST.get('resolution', '').strip()
        if resolution:
            dispute.status = 'resolved'
            dispute.resolution = resolution
            dispute.resolved_by = request.user
            dispute.resolved_at = timezone.now()
            dispute.save()
            
            messages.success(request, 'Dispute resolved successfully')
            return redirect('dispute_detail', dispute_id=dispute.id)
        else:
            messages.error(request, 'Please provide a resolution')
    
    return render(request, 'disputes/resolve_dispute.html', {'dispute': dispute})

@login_required
def escalate_dispute(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id, complainant=request.user)
    
    if request.method == 'POST':
        if dispute.status == 'resolved':
            dispute.status = 'escalated'
            dispute.save()
            messages.success(request, 'Dispute has been escalated to admin')
        else:
            messages.error(request, 'Only resolved disputes can be escalated')
    
    return redirect('dispute_detail', dispute_id=dispute.id)
