from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.cart.models import CartItem
from apps.products.models import Product
from apps.payments.models import Payment
from apps.reviews.models import Review
from notifications.signals import notify  # 添加这一行导入语句

# Viewset for Order, showing orders for the logged-in buyer
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({"message": "Order has been cancelled"})
        return Response({"error": "Only pending orders can be cancelled"}, status=400)

# Checkout functionality
@login_required
def checkout(request):
    # Check if it's a buy now purchase
    buy_now_product_id = request.GET.get('buy_now')
    
    if buy_now_product_id:
        # Buy now mode
        try:
            product = Product.objects.get(id=buy_now_product_id)
            cart_item = CartItem.objects.get(user=request.user, product=product)
            cart_items = [cart_item]
            total_price = cart_item.total_price
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Product does not exist or has been removed from cart')
            return redirect('home')
    else:
        # Regular cart checkout
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('view_cart')
        
        total_price = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        payment_method = request.POST.get('payment_method', 'balance')
        notes = request.POST.get('notes', '')
        
        # Check if balance is sufficient
        if payment_method == 'balance' and request.user.balance < total_price:
            messages.error(request, 'Your account balance is insufficient')
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'user_balance': request.user.balance
            })
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                buyer=request.user,
                status='pending',
                shipping_address=shipping_address,
                payment_method=payment_method,
                notes=notes
            )
            
            # Add order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # If paying with balance, deduct immediately and update order status
            if payment_method == 'balance':
                # Deduct balance
                request.user.balance -= total_price
                request.user.save()
                
                # Create payment record
                Payment.objects.create(
                    user=request.user,
                    order=order,
                    amount=total_price,
                    payment_method=payment_method,
                    status='completed'
                )
                
                # Update order status
                order.status = 'paid'
                order.payment_status = 'paid'
                order.save()
                
                # 更新所有订单中商品的状态为sold
                for item in order.items.all():
                    product = item.product
                    product.status = 'sold'
                    product.save(update_fields=['status'])
                
                # Clear cart (if buy now, only delete related product)
                if buy_now_product_id:
                    CartItem.objects.filter(user=request.user, product_id=buy_now_product_id).delete()
                else:
                    CartItem.objects.filter(user=request.user).delete()
                
                messages.success(request, 'Order payment successful!')
                return redirect('order_detail', order_id=order.id)
            
            # Other payment methods (not implemented)
            messages.info(request, 'Please complete payment')
            return redirect('order_detail', order_id=order.id)
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_balance': request.user.balance,
        'is_buy_now': bool(buy_now_product_id)
    })

# Order history
@login_required
def order_history(request):

    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

# Order details
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    order_items = order.items.all().select_related('product')
    
    # Check if user has already reviewed each product
    from apps.reviews.models import Review
    for item in order_items:
        item.has_reviewed = Review.objects.filter(
            product=item.product, 
            reviewer=request.user
        ).exists()
    
    # Check if user has already reviewed the seller
    from apps.reviews.models import SellerReview
    has_reviewed_seller = False
    if order_items:
        seller = order_items[0].product.seller
        has_reviewed_seller = SellerReview.objects.filter(
            seller=seller,
            reviewer=request.user
        ).exists()
    
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'has_reviewed_seller': has_reviewed_seller
    })

# Cancel order
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Can only cancel pending orders
    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be cancelled')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # If already paid, refund balance
        if order.payment_status == 'paid' and order.payment_method == 'balance':
            with transaction.atomic():
                # Refund balance
                total_price = order.total_price
                request.user.balance += total_price
                request.user.save()
                
                # Update payment record
                payment = Payment.objects.filter(order=order, status='completed').first()
                if payment:
                    payment.status = 'refunded'
                    payment.save()
                
                # Update order status
                order.status = 'cancelled'
                order.payment_status = 'refunded'
                order.save()
                
                messages.success(request, f'Order cancelled, £{total_price} has been refunded to your account')
        else:
            # Unpaid orders can be cancelled directly
            order.status = 'cancelled'
            order.save()
            messages.success(request, 'Order has been cancelled')
    
    return redirect('order_detail', order_id=order.id)

# 在process_payment函数中添加更新商品状态的代码
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    if request.method == 'POST':
        payment_method = 'balance'  # 新增支付方式定义
        total_price = order.total_price  # 新增总价定义
        
        if payment_method == 'balance':
            try:
                with transaction.atomic():
                    # 扣除余额
                    request.user.balance -= total_price
                    request.user.save()
                    
                    # 创建支付记录
                    Payment.objects.create(
                        user=request.user,
                        amount=total_price,
                        payment_type='purchase',
                        status='completed',
                        order=order
                    )
                    
                    # 更新订单状态
                    order.mark_as_paid()
                    
                    # 更新商品状态并发送通知
                    for item in order.items.all():
                        product = item.product
                        product.status = 'sold'
                        product.save(update_fields=['status'])
                        
                        # 发送实时通知给卖家
                        notify.send(
                            request.user,
                            recipient=product.seller,
                            verb='sold',
                            target=product,
                            description=f'Your product {product.title} has been purchased by {request.user.username}'
                        )
                    
                    # 清理购物车（移动到事务中）
                    CartItem.objects.filter(user=request.user).delete()
                    
                    messages.success(request, 'Order placed successfully!')
                    return redirect('order_detail', order_id=order.id)
            
            except Exception as e:
                logger.error(f"Order processing failed: {str(e)}")
                messages.error(request, 'Payment processing failed. Please try again.')
                return redirect('checkout')

        # 支付成功后，更新订单和商品状态
        order.status = 'paid'
        order.payment_status = 'paid'
        order.save()
        
        # 更新所有订单中商品的状态为sold
        for item in order.items.all():
            product = item.product
            product.status = 'sold'
            product.save(update_fields=['status'])
        
        # 发送通知给卖家
        notify.send(
            request.user,
            recipient=product.seller,
            verb='sold',
            target=product,
            description=f'Your product {product.title} has been sold'
        )
    
    # 通知卖家
    from notifications.signals import notify
    notify.send(
        request.user,
        recipient=product.seller,
        verb='sold',
        target=product,
        description=f'Your product {product.title} has been sold'
    )
    
    # Clear cart
    if buy_now_product_id:
        CartItem.objects.filter(user=request.user, product__id=buy_now_product_id).delete()
    else:
        CartItem.objects.filter(user=request.user).delete()
    
    messages.success(request, 'Order placed successfully!')
    return redirect('order_detail', order_id=order.id)

# 添加导入
from apps.notifications.utils import notify_seller


@login_required
def complete_order(request, order_id):
    """买家确认收货"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # 验证订单状态
    if order.status != 'shipped':
        messages.error(request, "This order is not ready to be completed")
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        # 更新订单状态
        order.status = 'completed'
        order.save()
        
        # 更新所有商品状态为已完成，并将货款转给卖家
        for item in order.items.all():
            product = item.product
            seller = product.seller
            
            # 确保商品状态为已完成
            if product.status != 'completed':
                product.status = 'completed'
                product.save(update_fields=['status'])
            
            # 计算卖家应得金额（商品小计）
            seller_amount = item.subtotal
            
            # 将金额转入卖家账户
            seller.balance += seller_amount
            seller.save()
            
            # 创建支付记录 - 只使用现有字段
            from apps.payments.models import Payment
            Payment.objects.create(
                user=seller,
                order=order,
                amount=seller_amount,
                payment_method='balance',
                status='completed',
                # 移除不存在的字段
                # payment_type='sale',
                # description=f'Payment for order #{order.id}, item: {product.title}'
            )
            
            # 通知卖家
            notify.send(
                request.user,
                recipient=seller,
                verb='completed',
                target=order,
                description=f'Order #{order.id} for your product {product.title} has been completed. ¥{seller_amount} has been added to your balance.'
            )
        
        # 只添加一次成功消息
        messages.success(request, "Order has been marked as completed and payment has been transferred to the seller")
        return redirect('order_detail', order_id=order_id)
    
    return redirect('order_detail', order_id=order_id)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order

@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {
        'orders': orders
    })


@login_required
def seller_orders(request):
    """卖家查看自己的订单"""
    # 获取当前用户作为卖家的所有订单项
    order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')
    
    # 按订单分组
    orders_dict = {}
    for item in order_items:
        if item.order.id not in orders_dict:
            orders_dict[item.order.id] = {
                'order': item.order,
                'items': [],
                'total': 0,
            }
        orders_dict[item.order.id]['items'].append(item)
        orders_dict[item.order.id]['total'] += item.subtotal
    
    seller_orders = list(orders_dict.values())
    
    return render(request, 'seller_orders.html', {
        'seller_orders': seller_orders
    })

@login_required
def ship_order(request, order_id):
    """卖家发货"""
    # 获取订单
    order = get_object_or_404(Order, id=order_id)
    
    # 验证权限（确保当前用户是订单中至少一个商品的卖家）
    order_items = order.items.filter(product__seller=request.user)
    if not order_items.exists():
        messages.error(request, "You don't have permission to ship this order")
        return redirect('my_products')
    
    # 验证订单状态
    if order.status != 'paid':
        messages.error(request, "This order is not ready for shipping")
        return redirect('my_products')
    
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '')
        
        # 更新订单状态
        order.status = 'shipped'
        order.tracking_number = tracking_number
        order.save()
        
        # 更新商品状态
        for item in order_items:
            product = item.product
            product.status = 'shipped'
            product.save(update_fields=['status'])
        
        # 通知买家
        from notifications.signals import notify
        notify.send(
            request.user,
            recipient=order.buyer,
            verb='shipped',
            target=order,
            description=f'Your order #{order.id} has been shipped. Tracking number: {tracking_number}'
        )
        
        messages.success(request, "Order has been marked as shipped")
        # 修改这里：使用reverse获取URL，然后添加查询参数
        from django.urls import reverse
        return redirect(reverse('my_products') + '?tab=sales')  # 重定向到销售选项卡
    
    return render(request, 'ship_order.html', {
        'order': order,
        'items': order_items
    })


def order_help(request):
    """订单流程帮助页面"""
    return render(request, 'order_help.html')
