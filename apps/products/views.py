from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

from apps.reviews.models import Review, SellerReview
from apps.orders.models import Order
from django.db.models import Avg
from apps.reviews.forms import ReviewForm

# REST API viewset for Product CRUD operations
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'seller']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

# View for posting a new product via a web form
class PostProductView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'
    
    def get(self, request):
        form = ProductForm()
        return render(request, 'post_product.html', {'form': form})
    
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.status = 'active'  # 设置默认状态
            product.save()
            messages.success(request, 'Product published successfully!')
            return redirect('home')
        return render(request, 'post_product.html', {'form': form})

@login_required
def my_products_view(request):
    user_products = Product.objects.filter(seller=request.user)
    return render(request, "my_products.html", {"user_products": user_products})

# Home view, displays product list with search and category filtering
class HomeView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query)
            )
        
        # Category filtering
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context

# Product detail view
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products (other products in the same category)
        related_products = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        context['related_products'] = related_products
        
        # 计算卖家评分
        from django.db.models import Avg
        from apps.reviews.models import SellerReview, Review
        
        # 卖家评分
        seller_reviews = SellerReview.objects.filter(seller=self.object.seller)
        context['avg_seller_rating'] = seller_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['seller_review_count'] = seller_reviews.count()
        
        # 产品评分
        product_reviews = Review.objects.filter(product=self.object)
        context['avg_product_rating'] = product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['product_review_count'] = product_reviews.count()
        
        return context

# Edit product view
class EditProductView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'
    
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        # Ensure only the seller can edit their own product
        if product.seller != request.user:
            messages.error(request, 'You do not have permission to edit this product')
            return redirect('product_detail', pk=pk)
        
        form = ProductForm(instance=product)
        return render(request, 'edit_product.html', {'form': form, 'product': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        # Ensure only the seller can edit their own product
        if product.seller != request.user:
            messages.error(request, 'You do not have permission to edit this product')
            return redirect('product_detail', pk=pk)
        
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', pk=pk)
        
        return render(request, 'edit_product.html', {'form': form, 'product': product})

# Delete product view
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Ensure only the seller can delete their own product
    if product.seller != request.user:
        messages.error(request, 'You do not have permission to delete this product')
        return redirect('product_detail', pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product has been successfully deleted')
        return redirect('home')
    
    # If not a POST request, redirect to product detail page
    return redirect('product_detail', pk=pk)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 修改这里：将 user 改为 buyer
    user_orders = Order.objects.filter(
        buyer=request.user,  # 这里改为 buyer 而不是 user
        status__in=['completed', 'delivered'],
        items__product=product
    ).distinct()
    
    if not user_orders.exists():
        messages.error(request, "You can only review products you have purchased.")
        return redirect('product_detail', product_id=product_id)
    
    # Check if user has already reviewed this product
    existing_review = Review.objects.filter(product=product, reviewer=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.reviewer = request.user
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm(instance=existing_review)
    
    return render(request, 'add_review.html', {
        'form': form,
        'product': product,
        'is_edit': existing_review is not None
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    # Check if current user can review this product
    can_review = False
    has_reviewed = False
    
    if request.user.is_authenticated:
        # Check if user has purchased this product
        user_orders = Order.objects.filter(
            buyer=request.user, 
            status__in=['completed', 'delivered'],
            items__product=product
        ).distinct()
        
        can_review = user_orders.exists()
        
        # Check if user has already reviewed this product
        has_reviewed = Review.objects.filter(product=product, reviewer=request.user).exists()
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    # Get seller rating
    seller_reviews = SellerReview.objects.filter(seller=product.seller)
    seller_review_count = seller_reviews.count()
    avg_seller_rating = seller_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'seller_review_count': seller_review_count,
        'avg_seller_rating': avg_seller_rating,
        'can_review': can_review,
        'has_reviewed': has_reviewed,
    }
    
    return render(request, 'product_detail.html', context)
