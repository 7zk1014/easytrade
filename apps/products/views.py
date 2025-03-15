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
