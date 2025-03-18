from rest_framework import viewsets, permissions
from .models import Review, SellerReview
from .serializers import ReviewSerializer
from .forms import ReviewForm, SellerReviewForm
from django.contrib.auth import get_user_model
from apps.orders.models import OrderItem, Order

# Get the custom user model
CustomUser = get_user_model()

# Viewset for product reviews
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return self.queryset

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg

from .models import Review
from .forms import ReviewForm
from apps.products.models import Product
from apps.orders.models import Order

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    has_purchased = Order.objects.filter(
        buyer=request.user,
        status__in=['completed', 'delivered'],
        items__product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, "You need to purchase and receive this product before you can review it.")
        return redirect('product_detail', pk=product_id)
    
    existing_review = Review.objects.filter(product=product, reviewer=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.reviewer = request.user
            review.verified_purchase = True
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm(instance=existing_review)
    
    return render(request, 'add_review.html', {
        'form': form,
        'product': product,
        'is_edit': existing_review is not None
    })

def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'product_reviews.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating
    })

@login_required
def add_seller_review(request, seller_id, order_id=None):
    seller = get_object_or_404(CustomUser, id=seller_id)
    order = None
    
    if order_id:
        order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Check if user has purchased from this seller
    has_purchased = Order.objects.filter(
        buyer=request.user,
        items__product__seller=seller,
        status__in=['delivered', 'completed']
    ).exists()
    
    # Check if user has already reviewed this seller
    existing_review = SellerReview.objects.filter(seller=seller, reviewer=request.user).first()
    
    if request.method == 'POST':
        form = SellerReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.seller = seller
            review.reviewer = request.user
            if order:
                review.order = order
            review.save()
            messages.success(request, 'Your review of the seller has been submitted successfully!')
            return redirect('seller_reviews', seller_id=seller.id)
    else:
        form = SellerReviewForm(instance=existing_review)
    
    return render(request, 'add_seller_review.html', {
        'form': form,
        'seller': seller,
        'existing_review': existing_review,
        'has_purchased': has_purchased,
        'order': order
    })

def seller_reviews(request, seller_id):
    """
    Display all reviews for a seller
    """
    seller = get_object_or_404(CustomUser, id=seller_id)
    reviews = SellerReview.objects.filter(seller=seller).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'seller_reviews.html', {
        'seller': seller,
        'reviews': reviews,
        'avg_rating': avg_rating
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import SellerReview
from django.db.models import Avg

def seller_profile(request, seller_id):
    """
    Display seller profile page with their information and reviews
    """
    User = get_user_model()
    seller = get_object_or_404(User, id=seller_id)
    
    # 获取卖家评价
    reviews = SellerReview.objects.filter(seller=seller).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'seller': seller,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'seller_profile.html', context)
