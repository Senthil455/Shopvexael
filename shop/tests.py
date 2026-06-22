from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Customer, Seller, Category, Brand, Product, Order, OrderItem, Coupon, ProductVariant, Review, Wishlist, Contact, CheckoutDetail, InventoryLog



class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.customer = Customer.objects.create(user=self.user, name='Test Customer', email='test@example.com')
        self.seller_user = User.objects.create_user(username='seller', password='testpass123', email='seller@example.com')
        self.seller = Seller.objects.create(user=self.seller_user, company_name='Test Seller')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.brand = Brand.objects.create(name='TestBrand', slug='testbrand')
        self.product = Product.objects.create(
            name='Test Product', seller=self.seller, category=self.category,
            brand=self.brand,             price=99.99, stock=10
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'testuser')

    def test_customer_email_field(self):
        field = Customer._meta.get_field('email')
        self.assertEqual(field.get_internal_type(), 'EmailField')

    def test_seller_str(self):
        self.assertEqual(str(self.seller), 'Test Seller')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_final_price_without_discount(self):
        self.assertEqual(self.product.final_price, 99.99)

    def test_product_final_price_with_discount(self):
        self.product.discount_price = 79.99
        self.assertEqual(self.product.final_price, 79.99)

    def test_product_stock_status_out_of_stock(self):
        self.product.stock = 0
        self.assertEqual(self.product.stock_status['label'], 'Out of Stock')

    def test_product_stock_status_critical(self):
        self.product.stock = 3
        self.assertEqual(self.product.stock_status['label'], 'Critical Stock')

    def test_product_stock_status_low(self):
        self.product.stock = 7
        self.assertEqual(self.product.stock_status['label'], 'Low Stock')

    def test_product_stock_status_in_stock(self):
        self.product.stock = 15
        self.assertEqual(self.product.stock_status['label'], 'In Stock')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Electronics')

    def test_brand_str(self):
        self.assertEqual(str(self.brand), 'TestBrand')

    def test_coupon_str(self):
        coupon = Coupon.objects.create(code='SAVE10', discount_percentage=10,
                                        valid_from='2026-01-01', valid_to='2026-12-31')
        self.assertEqual(str(coupon), 'SAVE10')

    def test_review_str(self):
        review = Review.objects.create(customer=self.customer, product=self.product,
                                        content='Great!', rating=5)
        self.assertIn(str(review.customer), str(review))

    def test_contact_email_field(self):
        field = Contact._meta.get_field('email')
        self.assertEqual(field.get_internal_type(), 'EmailField')

    def test_checkoutdetail_total_amount_field(self):
        field = CheckoutDetail._meta.get_field('total_amount')
        self.assertEqual(field.get_internal_type(), 'DecimalField')

    def test_inventory_log_creation(self):
        log = InventoryLog.objects.create(
            product=self.product, action='MANUAL', quantity_changed=10,
            previous_stock=0, new_stock=10
        )
        self.assertEqual(log.action, 'MANUAL')
        self.assertEqual(log.new_stock, 10)

    def test_order_get_cart_total_no_items(self):
        order = Order.objects.create(customer=self.customer)
        self.assertEqual(order.get_cart_total, 0)

    def test_order_get_cart_items_no_items(self):
        order = Order.objects.create(customer=self.customer)
        self.assertEqual(order.get_cart_items, 0)

    def test_product_variant_str(self):
        variant = ProductVariant.objects.create(product=self.product, color='Red', size='M')
        self.assertIn('Red', str(variant))

    def test_wishlist_str(self):
        wishlist = Wishlist.objects.create(customer=self.customer, product=self.product)
        self.assertIn(str(self.customer), str(wishlist))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        Customer.objects.create(user=self.user, name='Test Customer', email='test@example.com')

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_page(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_success(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, '/')

    def test_login_post_failure(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is incorrect')

    def test_register_page(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_success(self):
        response = self.client.post('/register/', {
            'username': 'newuser', 'full_name': 'New User',
            'email': 'new@example.com', 'phone_number': '1234567890',
            'password1': 'testpass123', 'password2': 'testpass123'
        })
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_contact_page(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_post_success(self):
        response = self.client.post('/contact/', {
            'name': 'John', 'email': 'john@example.com',
            'phone': '1234567890', 'desc': 'Hello'
        })
        self.assertContains(response, 'alert')
        self.assertTrue(Contact.objects.filter(name='John').exists())

    def test_register_duplicate_email_rejected(self):
        response = self.client.post('/register/', {
            'username': 'anotheruser', 'full_name': 'Another User',
            'email': 'test@example.com', 'phone_number': '',
            'password1': 'testpass123', 'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'email already exists')
        self.assertFalse(User.objects.filter(username='anotheruser').exists())

    def test_register_password_mismatch(self):
        response = self.client.post('/register/', {
            'username': 'user1', 'full_name': 'User',
            'email': 'user@example.com', 'phone_number': '',
            'password1': 'pass1', 'password2': 'pass2'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')

    def test_cart_page_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/login/')
        self.assertRedirects(response, '/')

    def test_authenticated_user_redirected_from_register(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/register/')
        self.assertRedirects(response, '/')

    def test_change_password_page_requires_auth(self):
        response = self.client.get('/change_password/')
        self.assertRedirects(response, '/login')

    def test_change_password_page_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/change_password/')
        self.assertEqual(response.status_code, 200)

    def test_change_password_post_success(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/change_password/', {
            'current_password': 'testpass123',
            'new_password': 'newsecurepass1',
            'confirm_password': 'newsecurepass1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password updated successfully')
        u = User.objects.get(username='testuser')
        self.assertTrue(u.check_password('newsecurepass1'))

    def test_change_password_wrong_current(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/change_password/', {
            'current_password': 'wrongpassword',
            'new_password': 'newsecurepass1',
            'confirm_password': 'newsecurepass1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Current password is incorrect')
        u = User.objects.get(username='testuser')
        self.assertTrue(u.check_password('testpass123'))

    def test_change_password_mismatch(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/change_password/', {
            'current_password': 'testpass123',
            'new_password': 'newpass1',
            'confirm_password': 'differentpass1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')
        u = User.objects.get(username='testuser')
        self.assertTrue(u.check_password('testpass123'))

    def test_change_password_too_short(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/change_password/', {
            'current_password': 'testpass123',
            'new_password': 'short',
            'confirm_password': 'short'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least 8 characters')
        u = User.objects.get(username='testuser')
        self.assertTrue(u.check_password('testpass123'))

    def test_wishlist_page_requires_auth(self):
        response = self.client.get('/wishlist/')
        self.assertRedirects(response, '/login/')

    def test_profile_page_requires_auth(self):
        response = self.client.get('/profile/')
        self.assertRedirects(response, '/login/')

    def test_cartdata_survives_user_email_change(self):
        """
        Regression test for issue #60: cartData must not crash with
        IntegrityError after the user's email is updated.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)

        original_customer = Customer.objects.get(user=self.user)
        original_email = original_customer.email

        self.user.email = 'updated_email@example.com'
        self.user.save()

        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)

        same_customer = Customer.objects.get(user=self.user)
        self.assertEqual(same_customer.id, original_customer.id)
        self.assertEqual(same_customer.email, original_email)

    def test_cartdata_survives_username_change(self):
        """
        Regression test: same as email change but for username, which
        is used as default for Customer.name.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)

        original_customer = Customer.objects.get(user=self.user)

        self.user.username = 'newname'
        self.user.save()

        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)

        same_customer = Customer.objects.get(user=self.user)
        self.assertEqual(same_customer.id, original_customer.id)
