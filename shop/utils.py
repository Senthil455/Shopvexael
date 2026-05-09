from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Notification

def send_custom_email(subject, template_name, context, recipient_list):
    """Helper to send HTML emails with plain-text fallback"""
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

def notify_order_update(order):
    """Sends email and creates in-app notification for order updates"""
    # Create In-App Notification
    Notification.objects.create(
        user=order.customer.user,
        title=f"Order Update: #{order.id}",
        message=f"Your order status has been updated to: {order.get_status_display()}",
        link=f"/tracker/?order_id={order.id}&email={order.customer.email}"
    )
    
    # Send Email
    subject = f"Order Update - Shopvexael Order #{order.id}"
    context = {'order': order}
    send_custom_email(subject, 'emails/order_update.html', context, [order.customer.email])

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
