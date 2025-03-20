def home(request):
    # Get the latest 8 active products

    latest_products = Product.objects.filter(status='active').order_by('-created_at')[:8]
    
    # Get all categories

    categories = Category.objects.all()
    
    return render(request, 'home.html', {
        'latest_products': latest_products,
        'categories': categories
    })