from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView
from apps.payments.views import payment_history, recharge_balance, request_refund, view_refund_request, process_refund, my_refund_requests
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import account_settings
from apps.users.views import user_profile, seller_profile  
from apps.products.views import HomeView, ProductDetailView, EditProductView, delete_product
from apps.cart.views import add_to_cart, view_cart, remove_from_cart, update_cart_item, buy_now
from apps.orders.views import checkout, order_history, order_detail, cancel_order
from apps.offers.views import make_offer, view_offers, accept_offer, reject_offer
from apps.messaging.views import send_message, view_messages, view_conversation
from apps.payments.views import create_payment_intent

urlpatterns = [
    path('admin/', admin.site.urls),
    # Built-in login/logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # API routes for custom apps
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')), 
    path('api/orders/', include('apps.orders.urls')),
    path('api/messaging/', include('apps.messaging.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('api/offers/', include('apps.offers.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('', HomeView.as_view(), name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/edit/<int:pk>/', EditProductView.as_view(), name='edit_product'),
    path('product/delete/<int:pk>/', delete_product, name='delete_product'),
    
    # Cart related
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('buy-now/', buy_now, name='buy_now'),
    
    # Order related
    path('checkout/', checkout, name='checkout'),
    path('orders/', order_history, name='order_history'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    
    # Payment related
    path('payments/', payment_history, name='payment_history'),
    path('recharge/', recharge_balance, name='recharge_balance'),
    
    # Refund related paths
    path('refund/request/<int:order_id>/', request_refund, name='request_refund'),
    path('refund/view/<int:request_id>/', view_refund_request, name='view_refund_request'),
    path('refund/process/<int:request_id>/', process_refund, name='process_refund'),
    path('refund/my-requests/', my_refund_requests, name='my_refund_requests'),
    
    # Offer related
    path('make-offer/', make_offer, name='make_offer'),
    path('offers/', view_offers, name='view_offers'),
    path('offer/accept/<int:offer_id>/', accept_offer, name='accept_offer'),
    path('offer/reject/<int:offer_id>/', reject_offer, name='reject_offer'),
    
    # Message related
    path('send-message/', send_message, name='send_message'),
    path('messages/', view_messages, name='view_messages'),
    path('messages/<int:user_id>/', view_conversation, name='view_conversation'),
    
    # Removed path('advanced-search/', TemplateView.as_view(template_name="advanced_search.html"), name='advanced_search'),
    path('favorites/', TemplateView.as_view(template_name="favorites.html"), name='favorites'),
    path('notifications/', include('apps.notifications.urls')),  # Add notification URL configuration
    path('report-support/', TemplateView.as_view(template_name="report_support.html"), name='report_support'),
    path('profile/', user_profile, name='profile'),
    path('post-product/', include('apps.products.urls_post')),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('payment/', TemplateView.as_view(template_name="payment.html"), name='payment'),
    path('account-settings/', account_settings, name='account_settings'),  
    path('reports/', include('apps.reports.urls')),
    # Add to urlpatterns
    path('products/', include('apps.products.urls')),  # Ensure this path is correct
    
    # Ensure there is a URL configuration for the seller profile page
    path('seller/<int:seller_id>/', seller_profile, name='seller_profile'),
]

# Add static files and media files URL configuration
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
path('api/payments/', include('apps.payments.urls')),
