from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from . inherit import cartData
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from functools import wraps
from .utils import notify_order_update, notify_seller_approval

def seller_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not Seller.objects.filter(user=request.user).exists():
            return redirect('/seller_signup/')
        return f(request, *args, **kwargs)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/')
        return f(request, *args, **kwargs)
    return wrap

def index(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.filter(is_deleted=False).select_related('category', 'brand', 'seller')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Advanced Filtering
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    discount = request.GET.get('discount')
    trending = request.GET.get('trending')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query) | Q(brand__name__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if discount:
        products = products.filter(discount_price__isnull=False)
    if trending:
        products = products.filter(is_trending=True)
        
    # Sorting
    if sort == 'new':
        products = products.order_by('-date_added')
    elif sort == 'popular':
        products = products.order_by('-views_count')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        # Default sort by featured/bestseller
        products = products.order_by('-is_featured', '-is_bestseller', '-date_added')
        
    context = {
        'products': products[:50], # Limit to 50 for performance
        'cartItems': cartItems,
        'categories': categories,
        'brands': brands,
        'query': query
    }
    return render(request, "index.html", context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image':product.image,
                },
                'quantity':cart[i]["quantity"],
                'get_total':total
            }
            items.append(item)
        except:
            pass
    return render(request, "cart.html", {'items':items, 'order':order, 'cartItems':cartItems})

def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    total = order.get_cart_total
    if request.method == "POST":
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        phone_number = request.POST['phone_number']
        payment = request.POST['payment']
        
        # Check if items exist
        if order.get_cart_items <= 0:
            return redirect('cart')
            
        shipping_adress = CheckoutDetail.objects.create(
            address=address, city=city, phone_number=phone_number, 
            state=state, zipcode=zipcode, customer=request.user.customer, 
            total_amount=total, order=order, payment=payment
        )
        
        order.complete = True
        order.status = 'Confirmed'
        order.save()
        
        # Reduce stock and log
        for item in order.orderitem_set.all():
            p = item.product
            prev_stock = p.stock
            p.stock = max(0, p.stock - item.quantity)
            p.save()
            
            InventoryLog.objects.create(
                product=p,
                action='PURCHASE',
                quantity_changed=-item.quantity,
                previous_stock=prev_stock,
                new_stock=p.stock,
                notes=f"Order #{order.id} placed"
            )
            
            # Notify Seller
            if p.seller:
                Notification.objects.create(
                    user=p.seller.user,
                    title="New Order Received",
                    message=f"You have a new order for {p.name} (Qty: {item.quantity})",
                    link=f"/seller_order_details/{order.id}/"
                )
        
        UpdateOrder.objects.create(order_id=order, desc="Your Order is Successfully Placed.")
        
        return render(request, "checkout.html", {'alert':True, 'id':order.id})
    return render(request, "checkout.html", {'items':items, 'order':order, 'cartItems':cartItems})

def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    print('Action:', action)
    print('productID:', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    update_order.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse({'message': 'Item was added', 'cartItems': order.get_cart_items}, safe=False)

def product_view(request, myid):
    product = Product.objects.filter(id=myid).first()
    feature = Feature.objects.filter(product=product)
    reviews = Review.objects.filter(product=product)
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    if request.method=="POST":
        if request.user.is_authenticated:
            content = request.POST.get('content')
            rating = request.POST.get('rating', 5)
            customer = request.user.customer
            review = Review(customer=customer, content=content, rating=rating, product=product, verified_purchase=True)
            review.save()
        return redirect(f"/product_view/{product.id}/")
    return render(request, "product_view.html", {'product':product, 'cartItems':cartItems, 'feature':feature, 'reviews':reviews})

def search(request):
    return redirect(f"/?q={request.GET.get('q', '')}")

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html", {'cartItems':cartItems})

def contact(request):
    if request.method=="POST":       
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'contact.html', {'alert':alert})
    return render(request, "contact.html")

def loggedin_contact(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method=="POST":       
        name = request.user
        email = request.user.email
        phone = request.user.customer.phone_number
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'loggedin_contact.html', {'alert':alert})
    return render(request, "loggedin_contact.html", {'cartItems':cartItems})

def tracker(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    cartItems = data['cartItems']
    order_id_get = request.GET.get('order_id')
    
    if request.method == "POST":
        try:
            order_id = request.POST.get('order_id')
            order = Order.objects.get(id=order_id, customer=request.user.customer)
            updates = UpdateOrder.objects.filter(order_id=order).order_by('datetime')
            
            response = []
            for update in updates:
                response.append({
                    'text': update.desc,
                    'time': update.datetime.strftime("%b %d, %Y %H:%M")
                })
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(response, safe=False)
                
            return render(request, "tracker.html", {
                'order': order, 
                'updates': updates, 
                'cartItems': cartItems
            })
        except Order.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Order not found'}, status=404)
            return render(request, "tracker.html", {'error': 'Order not found', 'cartItems': cartItems})

    return render(request, "tracker.html", {'cartItems': cartItems, 'order_id_get': order_id_get})

def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":   
            username = request.POST['username']
            full_name=request.POST['full_name']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            phone_number = request.POST['phone_number']
            email = request.POST['email']

            if password1 != password2:
                alert = True
                return render(request, "register.html", {'alert':alert})
            
            user = User.objects.create_user(username=username, password=password1, email=email)
            customers = Customer.objects.create(user=user, name=full_name, phone_number=phone_number, email=email)
            user.save()
            customers.save()
            
            login(request, user)
            return redirect("/")
    return render(request, "register.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                alert = True
                return render(request, "login.html", {"alert":alert})
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect("/")

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    data = cartData(request)
    cartItems = data['cartItems']
    customer = request.user.customer
    w_items = Wishlist.objects.filter(customer=customer)
    return render(request, 'wishlist.html', {'w_items': w_items, 'cartItems': cartItems})

def add_wishlist(request, myid):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == "POST":
            return JsonResponse({'status': 'unauthenticated'})
        return redirect('/login/')
    product = Product.objects.get(id=myid)
    obj, created = Wishlist.objects.get_or_create(customer=request.user.customer, product=product)
    if not created:
        obj.delete()
        status = 'removed'
    else:
        status = 'added'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == "POST":
        return JsonResponse({'status': status})
    return redirect(f'/product_view/{myid}/')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    data = cartData(request)
    cartItems = data['cartItems']
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-date_ordered')
    return render(request, 'profile.html', {'orders': orders, 'cartItems': cartItems, 'customer': customer})

def generic_placeholder(request, page_title):
    data = cartData(request)
    cartItems = data['cartItems']
    return render(request, 'placeholder.html', {'page_title': page_title, 'cartItems': cartItems})

def seller_signup(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if Seller.objects.filter(user=request.user).exists():
        return redirect('/seller_dashboard/')
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        description = request.POST.get('description')
        if company_name and description:
            Seller.objects.create(user=request.user, company_name=company_name, description=description, verified=False)
            return redirect('/seller_dashboard/')
        else:
            return render(request, 'seller_signup.html', {'alert': True, 'cartItems': cartItems})
    return render(request, 'seller_signup.html', {'cartItems': cartItems})

@seller_required
def seller_dashboard(request):
    seller = Seller.objects.get(user=request.user)
    data = cartData(request)
    cartItems = data['cartItems']
    
    seller_products = Product.objects.filter(seller=seller, is_deleted=False)
    total_products = seller_products.count()
    
    seller_order_items = OrderItem.objects.filter(product__seller=seller, order__complete=True)
    total_sales = sum([item.get_total for item in seller_order_items])
    
    order_ids = seller_order_items.values_list('order_id', flat=True).distinct()
    total_orders = len(order_ids)
    
    recent_orders = Order.objects.filter(id__in=order_ids).order_by('-date_ordered')[:5]
    
    # Inventory Alerts
    low_stock_products = seller_products.filter(stock__lt=10)
    
    context = {
        'seller': seller,
        'cartItems': cartItems,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'seller_dashboard.html', context)

@seller_required
def seller_products(request):
    seller = Seller.objects.get(user=request.user)
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.filter(seller=seller, is_deleted=False).order_by('-date_added')
    return render(request, 'seller_products.html', {'seller': seller, 'products': products, 'cartItems': cartItems})

@seller_required
def seller_add_product(request):
    seller = Seller.objects.get(user=request.user)
    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    brands = Brand.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        brand_id = request.POST.get('brand')
        short_description = request.POST.get('short_description')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        stock = request.POST.get('stock')
        tags = request.POST.get('tags')
        image = request.FILES.get('image')
        
        offer_percentage = 0
        if price and discount_price:
            p = float(price)
            dp = float(discount_price)
            if p > dp:
                offer_percentage = ((p - dp) / p) * 100
        
        product = Product.objects.create(
            seller=seller, name=name, sku=sku, category_id=category_id,
            subcategory_id=subcategory_id if subcategory_id else None,
            brand_id=brand_id, short_description=short_description,
            description=description, price=price,
            discount_price=discount_price if discount_price else None,
            offer_percentage=offer_percentage, stock=stock, tags=tags, image=image
        )
        
        InventoryLog.objects.create(
            product=product,
            action='MANUAL',
            quantity_changed=stock,
            previous_stock=0,
            new_stock=stock,
            notes="Initial stock on product creation"
        )
        
        return redirect('/seller_products/')
    context = {
        'seller': seller, 'cartItems': cartItems, 'categories': categories,
        'subcategories': subcategories, 'brands': brands
    }
    return render(request, 'seller_add_product.html', context)

@admin_required
def admin_dashboard(request):
    data = cartData(request)
    cartItems = data['cartItems']
    seller_count = Seller.objects.count()
    customer_count = Customer.objects.count()
    unverified_sellers = Seller.objects.filter(verified=False)
    pending_approvals = unverified_sellers.count()
    all_orders = Order.objects.filter(complete=True).order_by('-date_ordered')
    pending_orders = all_orders.count()
    total_revenue = sum([order.get_cart_total for order in all_orders])
    platform_commission = float(total_revenue) * 0.1
    new_today = User.objects.filter(date_joined__date=now().date()).count()
    context = {
        'cartItems': cartItems, 'seller_count': seller_count, 'customer_count': customer_count,
        'unverified_sellers': unverified_sellers, 'pending_approvals': pending_approvals,
        'all_orders': all_orders[:10], 'pending_orders': pending_orders,
        'total_revenue': total_revenue, 'platform_commission': platform_commission, 'new_today': new_today
    }
    return render(request, 'admin_dashboard.html', context)

@seller_required
def seller_orders(request):
    seller = Seller.objects.get(user=request.user)
    data = cartData(request)
    cartItems = data['cartItems']
    order_items = OrderItem.objects.filter(product__seller=seller, order__complete=True)
    order_ids = order_items.values_list('order_id', flat=True).distinct()
    orders_qs = Order.objects.filter(id__in=order_ids).order_by('-date_ordered')
    
    order_search = request.GET.get('order_search')
    if order_search:
        orders_qs = orders_qs.filter(Q(id__icontains=order_search) | Q(customer__name__icontains=order_search))
    
    orders_data = []
    for order in orders_qs:
        items = order_items.filter(order=order)
        seller_total = sum([item.get_total for item in items])
        orders_data.append({'order': order, 'items': items, 'seller_total': seller_total})
    
    context = {'seller': seller, 'orders': orders_data, 'cartItems': cartItems}
    return render(request, 'seller_orders.html', context)

@seller_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')
        tracking_number = data.get('tracking_number')
        seller_notes = data.get('seller_notes')
        
        order = get_object_or_404(Order, id=order_id)
        old_status = order.status
        order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        if seller_notes:
            order.seller_notes = seller_notes
        order.save()
        
        UpdateOrder.objects.create(order_id=order, desc=f"Order Status Updated: {new_status}")
        
        # Stock restoration on Cancel
        if new_status == 'Cancelled' and old_status != 'Cancelled':
            items = OrderItem.objects.filter(order=order)
            for item in items:
                p = item.product
                prev_stock = p.stock
                p.stock += item.quantity
                p.save()
                
                InventoryLog.objects.create(
                    product=p,
                    action='REFUND',
                    quantity_changed=item.quantity,
                    previous_stock=prev_stock,
                    new_stock=p.stock,
                    notes=f"Order #{order.id} cancelled - stock restored"
                )
        
        # Centralized Notification System
        notify_order_update(order)
        
        return JsonResponse({'status': 'success', 'new_status': new_status})
    return JsonResponse({'status': 'error'}, status=400)

@seller_required
def seller_order_details(request, order_id):
    seller = Seller.objects.get(user=request.user)
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order, product__seller=seller)
    seller_total = sum([item.get_total for item in items])
    shipping = CheckoutDetail.objects.filter(order=order).first()
    tracking_history = UpdateOrder.objects.filter(order_id=order).order_by('-datetime')
    context = {
        'order': order, 'items': items, 'seller_total': seller_total,
        'shipping': shipping, 'tracking_history': tracking_history, 'seller': seller
    }
    return render(request, 'seller_order_details.html', context)

@seller_required
def seller_edit_product(request, product_id):
    seller = Seller.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id, seller=seller)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.sku = request.POST.get('sku')
        product.category_id = request.POST.get('category')
        product.brand_id = request.POST.get('brand')
        product.short_description = request.POST.get('short_description')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') if request.POST.get('discount_price') else None
        
        old_stock = product.stock
        new_stock = int(request.POST.get('stock', 0))
        if old_stock != new_stock:
            InventoryLog.objects.create(
                product=product,
                action='MANUAL',
                quantity_changed=new_stock - old_stock,
                previous_stock=old_stock,
                new_stock=new_stock,
                notes="Stock updated via edit product page"
            )
        product.stock = new_stock
        
        product.tags = request.POST.get('tags')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        return redirect('/seller_products/')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    context = {'product': product, 'categories': categories, 'brands': brands, 'cartItems': cartData(request)['cartItems']}
    return render(request, 'seller_edit_product.html', context)

@seller_required
def seller_delete_product(request, product_id):
    seller = Seller.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id, seller=seller)
    product.is_deleted = True
    product.save()
    
    # Remove from wishlists
    Wishlist.objects.filter(product=product).delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == "POST":
        return JsonResponse({'status': 'success', 'message': 'Product deleted successfully'})
    return redirect('/seller_products/')

@seller_required
def seller_analytics(request):
    seller = Seller.objects.get(user=request.user)
    data = cartData(request)
    cartItems = data['cartItems']
    
    seller_order_items = OrderItem.objects.filter(product__seller=seller, order__complete=True)
    total_revenue = sum([item.get_total for item in seller_order_items])
    
    order_ids = seller_order_items.values_list('order_id', flat=True).distinct()
    total_orders = len(order_ids)
    
    total_customers = Order.objects.filter(id__in=order_ids).values('customer').distinct().count()
    
    # Simple growth calculation (this month vs last month)
    this_month = now().month
    last_month_revenue = sum([item.get_total for item in seller_order_items.filter(order__date_ordered__month=this_month-1)])
    this_month_revenue = sum([item.get_total for item in seller_order_items.filter(order__date_ordered__month=this_month)])
    
    growth = 0
    if last_month_revenue > 0:
        growth = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
        
    context = {
        'seller': seller, 
        'cartItems': cartItems, 
        'total_revenue': total_revenue,
        'total_orders': total_orders, 
        'total_customers': total_customers,
        'this_month_revenue': this_month_revenue,
        'growth': round(growth, 1)
    }
    return render(request, 'seller_analytics.html', context)

# --- NEW VIEWS ---

@seller_required
def seller_reviews(request):
    seller = Seller.objects.get(user=request.user)
    reviews = Review.objects.filter(product__seller=seller).order_by('-datetime')
    
    if request.method == "POST":
        review_id = request.POST.get('review_id')
        reply = request.POST.get('reply')
        review = get_object_or_404(Review, id=review_id, product__seller=seller)
        review.seller_reply = reply
        review.save()
        return redirect('/seller_reviews/')
        
    return render(request, 'seller_reviews.html', {
        'seller': seller, 
        'reviews': reviews, 
        'cartItems': cartData(request)['cartItems']
    })

@seller_required
def seller_inventory(request):
    seller = Seller.objects.get(user=request.user)
    products = Product.objects.filter(seller=seller, is_deleted=False).order_by('stock')
    logs = InventoryLog.objects.filter(product__seller=seller).order_by('-created_at')[:20]
    return render(request, 'seller_inventory.html', {
        'seller': seller, 
        'products': products, 
        'logs': logs,
        'cartItems': cartData(request)['cartItems']
    })

@seller_required
def update_stock(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_stock = int(data.get('stock', 0))
        seller = Seller.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id, seller=seller)
        
        old_stock = product.stock
        product.stock = new_stock
        product.save()
        
        InventoryLog.objects.create(
            product=product,
            action='RESTOCK' if new_stock > old_stock else 'MANUAL',
            quantity_changed=new_stock - old_stock,
            previous_stock=old_stock,
            new_stock=new_stock,
            notes="Stock updated via inventory quick-edit"
        )
        
        return JsonResponse({'status': 'success', 'new_stock': new_stock})
    return JsonResponse({'status': 'error'}, status=400)

@seller_required
def seller_settings(request):
    seller = Seller.objects.get(user=request.user)
    if request.method == 'POST':
        seller.company_name = request.POST.get('company_name')
        seller.description = request.POST.get('description')
        seller.save()
        
        user = request.user
        user.email = request.POST.get('email')
        user.save()
        
        customer = user.customer
        customer.name = request.POST.get('full_name')
        customer.phone_number = request.POST.get('phone_number')
        customer.save()
        
        return render(request, 'seller_settings.html', {'seller': seller, 'success': True, 'cartItems': cartData(request)['cartItems']})
        
    return render(request, 'seller_settings.html', {
        'seller': seller, 
        'cartItems': cartData(request)['cartItems']
    })

@seller_required
def seller_restore_products(request):
    seller = Seller.objects.get(user=request.user)
    products = Product.objects.filter(seller=seller, is_deleted=True).order_by('-date_added')
    return render(request, 'seller_restore_products.html', {
        'seller': seller, 
        'products': products,
        'cartItems': cartData(request)['cartItems']
    })

@seller_required
def seller_restore_action(request, product_id):
    seller = Seller.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id, seller=seller)
    product.is_deleted = False
    product.save()
    return redirect('/seller_restore_products/')

@admin_required
def approve_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.verified = True
    seller.save()
    
    notify_seller_approval(seller)
    
    return redirect('/admin_dashboard/')

@admin_required
def reject_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    # We could delete or just keep unverified. For now, let's keep unverified but notify.
    Notification.objects.create(
        user=seller.user,
        title="Account Verification Update",
        message="Your seller verification request was not approved. Please contact support for more details.",
        link="/contact/"
    )
    return redirect('/admin_dashboard/')

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read when visiting page
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'notifications.html', {
        'notifications': notifs,
        'cartItems': cartData(request)['cartItems']
    })

@seller_required
def seller_analytics_data(request):
    seller = Seller.objects.get(user=request.user)
    days = int(request.GET.get('days', 7))
    start_date = now() - timedelta(days=days)
    
    # Revenue by Day
    sales_data = OrderItem.objects.filter(
        product__seller=seller, 
        order__complete=True,
        order__date_ordered__gte=start_date
    ).annotate(
        date=TruncDate('order__date_ordered')
    ).values('date').annotate(
        revenue=Sum(models.F('quantity') * models.F('product__price')), # Simplified for speed
        orders=Count('order', distinct=True)
    ).order_by('date')
    
    labels = []
    revenue = []
    orders = []
    
    for entry in sales_data:
        labels.append(entry['date'].strftime("%b %d"))
        revenue.append(float(entry['revenue']))
        orders.append(entry['orders'])
        
    return JsonResponse({
        'labels': labels,
        'revenue': revenue,
        'orders': orders
    })

def ajax_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
        
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(category__name__icontains=query),
        is_deleted=False
    )[:5]
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image': p.image.url if p.image else '',
            'url': f'/product_view/{p.id}/'
        })
        
    return JsonResponse(results, safe=False)
