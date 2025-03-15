from django.contrib import admin
from .models import Review, SellerReview

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'verified_purchase', 'created_at')
    list_filter = ('rating', 'verified_purchase', 'created_at')
    search_fields = ('product__title', 'reviewer__username', 'comment')
    date_hierarchy = 'created_at'
    
    # 添加自定义过滤器
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.GET.get('verified_only'):
            queryset = queryset.filter(verified_purchase=True)
        return queryset
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['verified_only'] = request.GET.get('verified_only', False)
        return super().changelist_view(request, extra_context=extra_context)

# SellerReviewAdmin保持不变
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ('seller', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('seller__username', 'reviewer__username', 'comment')
    date_hierarchy = 'created_at'

admin.site.register(Review, ReviewAdmin)
admin.site.register(SellerReview, SellerReviewAdmin)
