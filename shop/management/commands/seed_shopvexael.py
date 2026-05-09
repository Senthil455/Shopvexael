import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import (Customer, Seller, Category, SubCategory, Brand, 
                        Product, ProductVariant, Review, Feature)

class Command(BaseCommand):
    help = 'Seeds the Shopvexael database with a massive realistic dataset.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding for Shopvexael V2...')
        
        # 1. Create Users
        users_created = []
        for i in range(1, 21):
            user, created = User.objects.get_or_create(username=f'user_{i}', defaults={'email': f'user_{i}@shopvexael.com'})
            if created:
                user.set_password('password123')
                user.save()
            users_created.append(user)

        # 2. Create Customers
        customers = []
        for user in users_created[:15]:
            customer, _ = Customer.objects.get_or_create(user=user, defaults={'name': f'Customer {user.username}', 'email': user.email, 'phone_number': '555-0000'})
            customers.append(customer)
            
        # 3. Create Sellers
        sellers = []
        for user in users_created[15:]:
            seller, _ = Seller.objects.get_or_create(user=user, defaults={'company_name': f'Shopvexael Partner {user.username}', 'verified': True, 'rating': random.uniform(3.5, 5.0)})
            sellers.append(seller)

        # 4. Create Categories & Subcategories
        cat_data = {
            'Electronics': ['Mobiles', 'Laptops', 'Audio', 'Cameras'],
            'Fashion': ['Men', 'Women', 'Kids', 'Accessories'],
            'Home Appliances': ['Kitchen', 'Cleaning', 'Heating', 'Smart Home'],
            'Gaming': ['Consoles', 'PC Components', 'Games', 'Accessories'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics'],
            'Sports': ['Fitness', 'Outdoor', 'Team Sports', 'Footwear']
        }
        
        categories_obj = {}
        subcats_obj = []
        for cat_name, subcats in cat_data.items():
            category, _ = Category.objects.get_or_create(name=cat_name, slug=cat_name.lower().replace(' ', '-'))
            categories_obj[cat_name] = category
            for sub in subcats:
                subcat, _ = SubCategory.objects.get_or_create(category=category, name=sub, slug=f"{category.slug}-{sub.lower().replace(' ', '-')}")
                subcats_obj.append(subcat)

        # 5. Create Brands
        brand_names = ['Apple', 'Samsung', 'Sony', 'Nike', 'Adidas', 'Dell', 'HP', 'Asus', 'LG', 'Puma', 'LG', 'Bose', 'Logitech', 'Nintendo']
        brands = []
        for b in brand_names:
            brand, _ = Brand.objects.get_or_create(name=b, slug=b.lower().replace(' ', '-'))
            brands.append(brand)

        # 6. Generate 200 Products
        self.stdout.write('Generating 200+ Products. This may take a moment...')
        products_created = []
        adjectives = ['Premium', 'Pro', 'Ultra', 'Smart', 'Elite', 'Advanced', 'Essential', 'Classic', 'Next-Gen', 'Gaming']
        nouns = ['Device', 'System', 'Gear', 'Kit', 'Bundle', 'Edition', 'Pack', 'Setup', 'Machine', 'Accessory']
        
        for i in range(1, 201):
            subcat = random.choice(subcats_obj)
            cat = subcat.category
            brand = random.choice(brands)
            seller = random.choice(sellers)
            
            name = f"{brand.name} {random.choice(adjectives)} {subcat.name[:-1]} {i} {random.choice(nouns)}"
            base_price = random.uniform(10.0, 2000.0)
            
            # 30% chance of discount
            discount_price = None
            offer_percentage = 0.0
            if random.random() < 0.3:
                offer_percentage = random.uniform(5.0, 50.0)
                discount_price = base_price * (1 - (offer_percentage / 100))

            product = Product.objects.create(
                name=name,
                seller=seller,
                category=cat,
                subcategory=subcat,
                brand=brand,
                price=round(base_price, 2),
                discount_price=round(discount_price, 2) if discount_price else None,
                offer_percentage=round(offer_percentage, 1),
                short_description=f"High quality {name} perfect for your everyday needs.",
                description=f"This is a massive extended description for {name}. It includes premium features, high durability, and is brought to you by {brand.name}.",
                stock=random.randint(0, 100),
                sku=f"SKU-{brand.name[:3].upper()}-{i:04d}",
                warranty_info="1 Year Manufacturer Warranty",
                delivery_time=random.choice(["1-2 Business Days (Prime)", "3-5 Business Days", "7 Days"]),
                return_policy="30 Days Returnable",
                is_trending=random.random() < 0.2,
                is_featured=random.random() < 0.1,
                is_bestseller=random.random() < 0.15,
                views_count=random.randint(10, 5000)
            )
            products_created.append(product)
            
            # Features
            for _ in range(3):
                Feature.objects.create(product=product, feature=f"Outstanding {random.choice(['Performance', 'Durability', 'Design', 'Battery Life', 'Quality'])}")

            # Variants (Colors/Sizes)
            if cat.name in ['Fashion', 'Sports']:
                for size in ['S', 'M', 'L']:
                    ProductVariant.objects.create(product=product, size=size, stock=random.randint(5, 20))
            elif cat.name in ['Electronics', 'Mobiles']:
                for color in ['Black', 'White', 'Silver']:
                    ProductVariant.objects.create(product=product, color=color, additional_price=random.choice([0, 10, 20]), stock=random.randint(5, 20))

            # Reviews
            for _ in range(random.randint(0, 8)):
                Review.objects.create(
                    customer=random.choice(customers),
                    product=product,
                    rating=random.randint(3, 5),
                    content="Great product! Highly recommended. Fast delivery.",
                    verified_purchase=True
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the Shopvexael database with 200 highly detailed products, categories, brands, variants, and reviews!'))
