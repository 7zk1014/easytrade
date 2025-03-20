from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm
from .forms import UserRegistrationForm
from django.contrib.auth import update_session_auth_hash, logout
from apps.products.models import Product
from apps.cart.models import CartItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from apps.reviews.models import SellerReview
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth import authenticate, login
from functools import wraps
from apps.users.models import Profile

User = get_user_model()

# User registration
def user_register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print("Registration form errors:", form.errors.as_json())
            # 修改为实际存在的模板路径
            return render(request, 'register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    # 修改为实际存在的模板路径
    return render(request, 'register.html', {'form': form})

# Account settings (integrated password change & profile)
def account_settings(request):
    if not request.user.is_authenticated:
        # When user is not logged in, show prompt page with next parameter
        return render(request, 'need_login.html', {'next': '/account-settings/'})

    if request.method == "POST":
        profile_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if "update_profile" in request.POST and profile_form.is_valid():
            profile_form.save()
            return redirect('account_settings')

        if "change_password" in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('account_settings')
    else:
        profile_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, "account_settings.html", {
        "profile_form": profile_form,
        "password_form": password_form
    })

# User logout
def user_logout(request):
    logout(request)
    return redirect('/login/')  # Redirect to login page after logout

@login_required
def user_profile(request):
    user = request.user
    user_products = Product.objects.filter(seller=user)
    print("User Products Count:", user_products.count())  # Debug info via terminal
    my_cart = CartItem.objects.filter(user=user)
    return render(request, "profile.html", {
        "user": user,
        "user_products": user_products,
        "my_cart": my_cart,
    })

@login_required
def seller_profile(request, seller_id):
    """View a seller's profile"""
    seller = get_object_or_404(User, id=seller_id)
    
    # Get all seller products, not just active ones
    all_products = Product.objects.filter(seller=seller)
    
    # Calculate total number of seller products
    total_products = all_products.count()
    
    # Get seller reviews
    reviews = SellerReview.objects.filter(seller=seller).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Add debug info
    print(f"Seller: {seller.username}, Total Products: {total_products}")
    for product in all_products:
        print(f"Product: {product.title}, Status: {product.status}")
    
    return render(request, 'seller_profile.html', {
        'seller': seller,
        'products': all_products,  # Pass all products, not just active ones
        'total_products': total_products,
        'reviews': reviews,
        'avg_rating': avg_rating
    })

# Check if user has permission to perform seller operations
def check_seller_permission(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Modified to allow 'both' role to perform seller operations
        if request.user.role in ['seller', 'both', 'admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You do not have permission to do this.")
            return redirect('home')
    return _wrapped_view

@login_required
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Process form submission
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        
        # Update Profile fields
        profile.phone = request.POST.get('phone')
        profile.bio = request.POST.get('bio')
        profile.address = request.POST.get('address')
        
        # Handle profile picture upload - modify this part
        if 'profile_picture' in request.FILES and request.FILES['profile_picture']:
            # Check if using CustomUser model
            if hasattr(user, 'profile_picture'):
                # Directly update user model's profile_picture field
                user.profile_picture = request.FILES['profile_picture']
            else:
                # Update Profile model's profile_picture field
                profile.profile_picture = request.FILES['profile_picture']
        
        # Save changes
        try:
            user.save()
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Update failed: {str(e)}')
        
        return redirect('profile')
    
    return render(request, 'edit_profile.html')

def user_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            context['username'] = username
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
                context['username'] = username
        
    return render(request, 'login.html', context)

