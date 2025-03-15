from rest_framework import viewsets, permissions
from .models import Message
from .serializers import MessageSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from apps.users.models import CustomUser
from apps.products.models import Product

# Viewset for messaging; users see messages they sent or received
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        product_id = request.POST.get('product_id', None)
        content = request.POST.get('content')
        
        if not recipient_id or not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Please provide recipient and message content'})
            messages.error(request, 'Please provide recipient and message content')
            return redirect('view_messages')
        
        try:
            recipient = CustomUser.objects.get(id=recipient_id)
            message = Message.objects.create(
                sender=request.user,
                receiver=recipient,
                content=content
            )
            
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    message.product = product
                    message.save()
                except Product.DoesNotExist:
                    pass
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': f'Message sent to {recipient.username}'})
            
            messages.success(request, f'Message sent to {recipient.username}')
            return redirect('view_conversation', user_id=recipient.id)
            
        except CustomUser.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Recipient does not exist'})
            messages.error(request, 'Recipient does not exist')
            return redirect('view_messages')
    
    return redirect('view_messages')

@login_required
def view_messages(request):
    # Get all conversations related to current user
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values('sender', 'receiver').distinct()
    
    # Organize conversation list
    users = set()
    for conv in conversations:
        if conv['sender'] == request.user.id:
            users.add(conv['receiver'])
        else:
            users.add(conv['sender'])
    
    conversation_users = CustomUser.objects.filter(id__in=users)
    
    return render(request, 'messages.html', {
        'conversation_users': conversation_users
    })

@login_required
def view_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    
    # Get conversation with specified user
    conversation = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # No need to mark messages as read since is_read field doesn't exist in the model
    
    return render(request, 'conversation.html', {
        'conversation': conversation,
        'other_user': other_user
    })
