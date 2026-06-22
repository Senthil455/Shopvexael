import logging
from functools import wraps
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from shop.models import Notification

logger = logging.getLogger(__name__)

def send_custom_email(subject, template_name, context, recipient_list):
    """Helper to send HTML emails with plain-text fallback"""
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        return True
    except Exception as e:
        logger.error("Email failed: %s", e)
        return False

def notify_order_update(order):
    """Sends email and creates in-app notification for order updates"""
    # Create In-App Notification
    Notification.objects.create(
        user=order.customer.user,
        title=f"Order Update: #{order.id}",
        message=f"Your order status has been updated to: {order.get_status_display()}",
        link=f"/tracker/?order_id={order.id}"
    )
    
    # Send Email
    subject = f"Order Update - Shopvexael Order #{order.id}"
    context = {'order': order}
    send_custom_email(subject, 'emails/order_update.html', context, [order.customer.email])

from django.core.cache import cache

# Simple in-memory rate limiter (per-view, per-IP)
# Deprecated: use cache-based rate_limit below for production deployments
_rate_limit_store = {}

def rate_limit(max_requests=10, window_seconds=60):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            key = f"ratelimit:{view_func.__name__}:{ip}"
            count = cache.get(key, 0)
            if count >= max_requests:
                return JsonResponse({'error': 'Rate limit exceeded. Try again later.'}, status=429)
            cache.set(key, count + 1, window_seconds)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def notify_seller_approval(seller):
    """Notifies seller about account approval"""
    Notification.objects.create(
        user=seller.user,
        title="Welcome to Shopvexael!",
        message="Your seller account has been approved. You can now list products.",
        link="/seller_dashboard/"
    )
    
    subject = "Welcome to Shopvexael - Seller Approved"
    context = {'seller': seller}
    send_custom_email(subject, 'emails/seller_welcome.html', context, [seller.user.email])
