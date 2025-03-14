from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView
from apps.payments.views import create_payment_intent
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import account_settings
from apps.users.views import user_profile


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
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/offers/', include('apps.offers.urls')),
    path('api/disputes/', include('apps.disputes.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Payment simulation route
    path('api/payments/create_intent/', create_payment_intent, name='create_payment_intent'),

    # Front-end pages (templates)
    path('', TemplateView.as_view(template_name="index.html"), name='home'),
    path('advanced-search/', TemplateView.as_view(template_name="advanced_search.html"), name='advanced_search'),
    path('favorites/', TemplateView.as_view(template_name="favorites.html"), name='favorites'),
    path('notifications/', TemplateView.as_view(template_name="notifications.html"), name='notifications'),
    path('report-support/', TemplateView.as_view(template_name="report_support.html"), name='report_support'),
    path('profile/', user_profile, name='profile'),
    path('post-product/', include('apps.products.urls_post')),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('payment/', TemplateView.as_view(template_name="payment.html"), name='payment'),
    path('account-settings/', account_settings, name='account_settings')
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
