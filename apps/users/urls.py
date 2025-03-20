from django.urls import path
from .views import user_register, account_settings, user_logout, user_profile, edit_profile

urlpatterns = [
    path('register/', user_register, name='register'), 
    path('account-settings/', account_settings, name='account_settings'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
