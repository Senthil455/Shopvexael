from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    rating = models.FloatField(default=0.0)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.FloatField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)

    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    offer_percentage = models.FloatField(default=0.0)

    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Base Image (Thumbnail)
    image = models.ImageField(upload_to="products/", default="")

    stock = models.IntegerField(default=10, db_index=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)

    warranty_info = models.CharField(max_length=200, null=True, blank=True)
    delivery_time = models.CharField(max_length=100, null=True, blank=True)
    return_policy = models.CharField(max_length=200, null=True, blank=True)

    tags = models.CharField(max_length=500, null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    country_of_origin = models.CharField(max_length=100, null=True, blank=True)

    views_count = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=now, db_index=True)

    is_trending = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_bestseller = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['-date_added', 'is_featured', 'is_bestseller']),
            models.Index(fields=['category', 'is_deleted']),
            models.Index(fields=['seller', 'is_deleted']),
        ]

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum([r.rating for r in reviews]) / len(reviews)
        return 0

    @property
    def stock_status(self):
        if self.stock <= 0:
            return {'label': 'Out of Stock', 'color': '#ef4444'}
        elif self.stock < 5:
            return {'label': 'Critical Stock', 'color': '#ef4444'}
        elif self.stock < 10:
            return {'label': 'Low Stock', 'color': '#f59e0b'}
        else:
            return {'label': 'In Stock', 'color': '#10b981'}


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_gallery/")

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    additional_price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"


class Feature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"{self.product} Feature: {self.description or ''}"


class Review(models.Model):
    RATING_CHOICES = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    seller_reply = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.customer} Review: {self.rating} stars for {self.product.name}"


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.customer} - {self.product}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
        ('Refunded', 'Refunded'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(default=now)
    complete = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    seller_notes = models.TextField(null=True, blank=True)
    coupon_applied = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        if self.coupon_applied and self.coupon_applied.active and self.coupon_applied.discount_percentage:
            discount = total * (self.coupon_applied.discount_percentage / 100)
            total -= discount
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.order)

    @property
    def get_total(self):
        base_price = self.product.final_price
        if self.variant:
            base_price += self.variant.additional_price
        return base_price * self.quantity


class UpdateOrder(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    desc = models.CharField(max_length=500)
    datetime = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.order_id)


class CheckoutDetail(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    payment = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(default=now)

    def __str__(self):
        return self.address


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    desc = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Payment {self.transaction_id or 'N/A'} - {self.get_method_display()} - {self.get_status_display()}"


class InventoryLog(models.Model):
    ACTION_CHOICES = (
        ('PURCHASE', 'Purchase'),
        ('REFUND', 'Refund / Cancellation'),
        ('MANUAL', 'Manual Adjustment'),
        ('RESTOCK', 'Restock'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name}: {self.action} ({self.quantity_changed:+d})"