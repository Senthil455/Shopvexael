import json
from shop.models import *

def cartData(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, email=request.user.email, name=request.user.username)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
    return {'cartItems':cartItems, 'items':items, 'order':order, 'unread_notifications': unread_notifications}