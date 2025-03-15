from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Offer
from .serializers import OfferSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from apps.products.models import Product
from apps.orders.models import Order, OrderItem  # 添加这一行导入 Order 和 OrderItem 模型

# Viewset for handling offers and seller responses
class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Offer.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        offer = self.get_object()
        if request.user == offer.product.seller:
            offer.offer_status = 'accepted'
            offer.save()
            return Response({'message': 'Offer accepted'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        offer = self.get_object()
        if request.user == offer.product.seller:
            offer.offer_status = 'rejected'
            offer.save()
            return Response({'message': 'Offer rejected'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

@login_required
def make_offer(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        offer_price = request.POST.get('offer_price')
        offer_message = request.POST.get('offer_message', '')
        
        if not product_id or not offer_price:
            messages.error(request, 'Please provide product ID and offer amount')
            return redirect('home')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if it's user's own product
            if product.seller == request.user:
                messages.error(request, 'You cannot make an offer on your own product')
                return redirect('product_detail', pk=product_id)
            
            # Create offer
            Offer.objects.create(
                product=product,
                buyer=request.user,
                offer_price=offer_price,
                message=offer_message
            )
            
            messages.success(request, f'You have successfully made an offer of ${offer_price} for {product.title}')
            return redirect('product_detail', pk=product_id)
            
        except Product.DoesNotExist:
            messages.error(request, 'Product does not exist')
            return redirect('home')
    
    return redirect('home')

@login_required
def view_offers(request):
    # Offers made as a buyer
    sent_offers = Offer.objects.filter(buyer=request.user).select_related('product').order_by('-created_at')
    
    # Offers received as a seller
    received_offers = Offer.objects.filter(product__seller=request.user).select_related('product', 'buyer').order_by('-created_at')
    
    return render(request, 'offers.html', {
        'sent_offers': sent_offers,
        'received_offers': received_offers
    })

@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, product__seller=request.user)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update offer status
                offer.offer_status = 'accepted'
                offer.save()
                
                # Update product price to match the accepted offer
                product = offer.product
                product.price = offer.offer_price
                product.save()
                
                messages.success(request, 'Offer accepted successfully')
        except Exception as e:
            messages.error(request, f'Error accepting offer: {str(e)}')
    
    # Return to the previous page without redirecting
    return redirect(request.META.get('HTTP_REFERER', 'view_offers'))

@login_required
def reject_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, product__seller=request.user)
    
    if request.method == 'POST':
        try:
            offer.offer_status = 'rejected'
            offer.save()
            messages.success(request, 'Offer rejected successfully')
        except Exception as e:
            messages.error(request, f'Error rejecting offer: {str(e)}')
    
    return redirect('view_offers')
