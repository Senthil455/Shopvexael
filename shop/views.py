from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from . inherit import cartData

from django.db.models import Q

def index(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all().select_related('category', 'brand', 'seller')
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
        shipping_adress = CheckoutDetail.objects.create(address=address, city=city, phone_number=phone_number, state=state, zipcode=zipcode, customer=request.user.customer, total_amount=total, order=order, payment=payment)
        shipping_adress.save()
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        id = order.id  
        alert = True
        return render(request, "checkout.html", {'alert':alert, 'id':id})
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
    # Redirect to index for all filtering and searching logic
    return redirect(f"/?q={request.GET.get('q', '')}")


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
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
    items = data['items']
    order = data['order']
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
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        order_id = request.POST['order_id']
        order = Order.objects.filter(id=order_id).first()
        order_items = OrderItem.objects.filter(order=order)
        update_order = UpdateOrder.objects.filter(order_id=order_id)
        print(update_order)
        return render(request, "tracker.html", {'order_items':order_items, 'update_order':update_order})
    return render(request, "tracker.html", {'cartItems':cartItems})


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
            
            # Auto login after registration
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
    
    # Check if user is already a seller
    if Seller.objects.filter(user=request.user).exists():
        return redirect('/seller_dashboard/')
        
    data = cartData(request)
    cartItems = data['cartItems']
    
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        description = request.POST.get('description')
        
        if company_name and description:
            Seller.objects.create(
                user=request.user,
                company_name=company_name,
                description=description,
                verified=False # Requires admin approval
            )
            return redirect('/seller_dashboard/')
        else:
            return render(request, 'seller_signup.html', {'alert': True, 'cartItems': cartItems})
            
    return render(request, 'seller_signup.html', {'cartItems': cartItems})


def seller_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('/seller_signup/')
        
    data = cartData(request)
    cartItems = data['cartItems']
    
    # Fetch real stats for the seller
    seller_products = Product.objects.filter(seller=seller)
    total_products = seller_products.count()
    
    # Fetch orders containing this seller's products
    # This is a bit complex in V1 schema, but in V2 we can filter OrderItems
    seller_order_items = OrderItem.objects.filter(product__seller=seller)
    total_sales = sum([item.get_total for item in seller_order_items])
    total_orders = Order.objects.filter(orderitem__product__seller=seller).distinct().count()
    recent_orders = Order.objects.filter(orderitem__product__seller=seller, complete=True).distinct().order_by('-date_ordered')[:5]
    
    context = {
        'seller': seller,
        'cartItems': cartItems,
        'total_products': total_products,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'seller_dashboard.html', context)


def seller_products(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('/seller_signup/')
        
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.filter(seller=seller).order_by('-date_added')
    
    return render(request, 'seller_products.html', {'seller': seller, 'products': products, 'cartItems': cartItems})


def seller_add_product(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('/seller_signup/')
        
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
        
        # Calculate offer percentage if discount price provided
        offer_percentage = 0
        if price and discount_price:
            p = float(price)
            dp = float(discount_price)
            if p > dp:
                offer_percentage = ((p - dp) / p) * 100

        product = Product.objects.create(
            seller=seller,
            name=name,
            sku=sku,
            category_id=category_id,
            subcategory_id=subcategory_id if subcategory_id else None,
            brand_id=brand_id,
            short_description=short_description,
            description=description,
            price=price,
            discount_price=discount_price if discount_price else None,
            offer_percentage=offer_percentage,
            stock=stock,
            tags=tags,
            image=image
        )
        return redirect('/seller_products/')
        
    context = {
        'seller': seller,
        'cartItems': cartItems,
        'categories': categories,
        'subcategories': subcategories,
        'brands': brands
    }
    return render(request, 'seller_add_product.html', context)


def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('/')
        
    data = cartData(request)
    cartItems = data['cartItems']
    
    # Advanced stats for the platform owner
    seller_count = Seller.objects.count()
    customer_count = Customer.objects.count()
    unverified_sellers = Seller.objects.filter(verified=False)
    pending_approvals = unverified_sellers.count()
    
    all_orders = Order.objects.filter(complete=True).order_by('-date_ordered')
    pending_orders = all_orders.count() # Mock count for now
    total_revenue = sum([order.get_cart_total for order in all_orders])
    
    new_today = User.objects.filter(date_joined__date=now().date()).count()
    
    context = {
        'cartItems': cartItems,
        'seller_count': seller_count,
        'customer_count': customer_count,
        'unverified_sellers': unverified_sellers,
        'pending_approvals': pending_approvals,
        'all_orders': all_orders[:10],
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'new_today': new_today
    }
    
    return render(request, 'admin_dashboard.html', context)

